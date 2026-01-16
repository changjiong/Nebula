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
from app.core.permissions import check_skill_permission, filter_skills_by_permission

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
    
    # Apply permission filtering based on user's department/roles
    all_skills = session.exec(query).all()
    accessible_skills = filter_skills_by_permission(current_user, all_skills)
    
    # Manual pagination after permission filter
    total = len(accessible_skills)
    paginated = accessible_skills[skip : skip + limit]
    
    return SkillsPublic(data=paginated, count=total)


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
        
    if not check_skill_permission(current_user, skill):
        raise HTTPException(status_code=403, detail="Not authorized to access this skill")
        
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
        
    if not check_skill_permission(current_user, skill):
        raise HTTPException(status_code=403, detail="Not authorized to access this skill")
        
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
        
    # Only creator or superuser can edit
    if not current_user.is_superuser and skill.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this skill")
    
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
        
    # Only creator or superuser can delete
    if not current_user.is_superuser and skill.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this skill")
    
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
        
    if not check_skill_permission(current_user, skill):
        raise HTTPException(status_code=403, detail="Not authorized to access this skill")
    
    import time
    start_time = time.time()
    
    try:
        from app.engine.executor import DAGScheduler, ParallelExecutor, Task
        from app.engine.tool_executor import get_tool_executor
        
        # 1. Parse workflow
        workflow = skill.workflow or {}
        nodes = workflow.get("nodes", [])
        output_mapping = workflow.get("output_mapping", {})
        
        if not nodes:
             # Empty workflow
             return SkillTestResult(
                success=True,
                result={"message": "Empty workflow", "input": request.params},
                latency_ms=(time.time() - start_time) * 1000,
                tool_results={}
             )

        # 2. Setup Executors
        scheduler = DAGScheduler()
        tool_executor = get_tool_executor(session)
        
        # Helper to resolve params from context
        def resolve_value(path: str, context: dict) -> Any:
            if not isinstance(path, str) or not path.startswith("$"):
                return path
            
            # Simple dot notation resolver: $.step1.data
            parts = path.lstrip("$.").split(".")
            current = context
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            return current

        def resolve_params(mapping: dict, context: dict) -> dict:
            resolved = {}
            for k, v in mapping.items():
                if isinstance(v, str) and v.startswith("$"):
                    resolved[k] = resolve_value(v, context)
                elif isinstance(v, dict):
                    resolved[k] = resolve_params(v, context)
                else:
                    resolved[k] = v
            return resolved

        # 3. Build DAG
        for node in nodes:
            node_id = node.get("id")
            tool_name = node.get("tool")
            params_mapping = node.get("params_mapping", {})
            depends_on = node.get("depends_on", [])
            
            # Create a closure for the task handler
            async def task_handler(ctx, nm=tool_name, pm=params_mapping):
                # Resolve args
                args = resolve_params(pm, ctx)
                # Execute tool
                return await tool_executor.execute(
                    tool_name=nm,
                    arguments=args,
                    user_id=str(current_user.id),
                )
            
            scheduler.add_task(
                task_id=node_id,
                name=f"{node_id} ({tool_name})",
                handler=task_handler,
                dependencies=depends_on
            )
            
        # 4. Execute
        parallel_executor = ParallelExecutor(scheduler=scheduler)
        # Initial context with input
        initial_context = {"input": request.params}
        
        # execution_results will contain "results": {node_id: output}
        exec_output = await parallel_executor.execute_all(initial_context)
        
        # 5. Process Output
        # Construct final output based on output_mapping
        final_result = {}
        if output_mapping:
            # Create a context that includes all step results for mapping
            # Context structure: { "input": ..., "step1": ..., "step2": ... }
            mapping_context = {"input": request.params, **exec_output}
            final_result = resolve_params(output_mapping, mapping_context)
        else:
            # Default: return all step results
            final_result = exec_output

        latency_ms = (time.time() - start_time) * 1000
        
        return SkillTestResult(
            success=True,
            result=final_result,
            latency_ms=latency_ms,
            tool_results=exec_output,
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return SkillTestResult(
            success=False,
            error=str(e),
            latency_ms=latency_ms,
        )
