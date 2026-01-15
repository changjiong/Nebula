"""
Skill CRUD API Routes

Provides endpoints for managing Skills (DAG workflows that orchestrate multiple Tools).
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Skill,
    SkillCreate,
    SkillPublic,
    SkillsPublic,
    SkillTestRequest,
    SkillTestResult,
    SkillUpdate,
)

router = APIRouter(prefix="/skills", tags=["skills"])


# ============ List / Search ============

@router.get("/", response_model=SkillsPublic)
async def list_skills(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str | None = Query(None, description="Filter by status"),
    category: str | None = Query(None, description="Filter by category"),
    search: str | None = Query(None, description="Search in name and description"),
) -> SkillsPublic:
    """List all skills with optional filtering."""
    query = select(Skill)
    
    if status:
        query = query.where(Skill.status == status)
    if category:
        query = query.where(Skill.category == category)
    if search:
        query = query.where(
            col(Skill.name).icontains(search) | col(Skill.description).icontains(search)
        )
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    count = session.exec(count_query).one()
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Skill.created_at.desc())
    skills = session.exec(query).all()
    
    return SkillsPublic(data=skills, count=count)


# ============ Get Single ============

@router.get("/{skill_id}", response_model=SkillPublic)
async def get_skill(
    session: SessionDep,
    current_user: CurrentUser,
    skill_id: uuid.UUID,
) -> Skill:
    """Get a single skill by ID."""
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.get("/by-name/{name}", response_model=SkillPublic)
async def get_skill_by_name(
    session: SessionDep,
    current_user: CurrentUser,
    name: str,
) -> Skill:
    """Get a single skill by name."""
    skill = session.exec(select(Skill).where(Skill.name == name)).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


# ============ Create ============

@router.post("/", response_model=SkillPublic)
async def create_skill(
    session: SessionDep,
    current_user: CurrentUser,
    skill_in: SkillCreate,
) -> Skill:
    """Create a new skill."""
    existing = session.exec(select(Skill).where(Skill.name == skill_in.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Skill with this name already exists")
    
    skill = Skill(
        **skill_in.model_dump(),
        created_by=current_user.id,
    )
    session.add(skill)
    session.commit()
    session.refresh(skill)
    
    return skill


# ============ Update ============

@router.patch("/{skill_id}", response_model=SkillPublic)
async def update_skill(
    session: SessionDep,
    current_user: CurrentUser,
    skill_id: uuid.UUID,
    skill_in: SkillUpdate,
) -> Skill:
    """Update a skill."""
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    if skill_in.name and skill_in.name != skill.name:
        existing = session.exec(select(Skill).where(Skill.name == skill_in.name)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Skill with this name already exists")
    
    update_data = skill_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(skill, key, value)
    
    skill.updated_at = datetime.utcnow()
    session.add(skill)
    session.commit()
    session.refresh(skill)
    
    return skill


# ============ Delete ============

@router.delete("/{skill_id}", response_model=Message)
async def delete_skill(
    session: SessionDep,
    current_user: CurrentUser,
    skill_id: uuid.UUID,
) -> Message:
    """Delete a skill."""
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    session.delete(skill)
    session.commit()
    
    return Message(message="Skill deleted successfully")


# ============ Test Skill ============

@router.post("/{skill_id}/test", response_model=SkillTestResult)
async def test_skill(
    session: SessionDep,
    current_user: CurrentUser,
    skill_id: uuid.UUID,
    request: SkillTestRequest,
) -> SkillTestResult:
    """Test a skill with sample parameters."""
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    import time
    start_time = time.time()
    
    try:
        # TODO: Implement actual skill execution via SkillExecutor
        result = {
            "message": f"Skill '{skill.name}' executed successfully (mock)",
            "input": request.params,
        }
        latency_ms = (time.time() - start_time) * 1000
        
        return SkillTestResult(
            success=True,
            result=result,
            latency_ms=latency_ms,
            tool_results={},
        )
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return SkillTestResult(
            success=False,
            error=str(e),
            latency_ms=latency_ms,
        )
