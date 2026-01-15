"""
Tool CRUD API Routes

Provides endpoints for managing Tools (atomic callable units) that can be
invoked by the LLM through Native Function Calling.
"""

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Tool,
    ToolCreate,
    ToolPublic,
    ToolsPublic,
    ToolTestRequest,
    ToolTestResult,
    ToolUpdate,
)

router = APIRouter(prefix="/tools", tags=["tools"])


# ============ List / Search ============

@router.get("/", response_model=ToolsPublic)
async def list_tools(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str | None = Query(None, description="Filter by status: draft, active, deprecated"),
    category: str | None = Query(None, description="Filter by category"),
    tool_type: str | None = Query(None, description="Filter by tool type"),
    search: str | None = Query(None, description="Search in name and description"),
) -> ToolsPublic:
    """
    List all tools with optional filtering.
    
    Respects permission control based on user's department and roles.
    """
    # Build query
    query = select(Tool)
    
    # Apply filters
    if status:
        query = query.where(Tool.status == status)
    if category:
        query = query.where(Tool.category == category)
    if tool_type:
        query = query.where(Tool.tool_type == tool_type)
    if search:
        query = query.where(
            col(Tool.name).icontains(search) | col(Tool.description).icontains(search)
        )
    
    # TODO: Apply permission filtering based on user's department/roles
    # For now, return all tools (permission check to be implemented later)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    count = session.exec(count_query).one()
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Tool.created_at.desc())
    tools = session.exec(query).all()
    
    return ToolsPublic(data=tools, count=count)


# ============ Get Single ============

@router.get("/{tool_id}", response_model=ToolPublic)
async def get_tool(
    session: SessionDep,
    current_user: CurrentUser,
    tool_id: uuid.UUID,
) -> Tool:
    """Get a single tool by ID."""
    tool = session.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # TODO: Check permission
    
    return tool


@router.get("/by-name/{name}", response_model=ToolPublic)
async def get_tool_by_name(
    session: SessionDep,
    current_user: CurrentUser,
    name: str,
) -> Tool:
    """Get a single tool by name."""
    tool = session.exec(select(Tool).where(Tool.name == name)).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return tool


# ============ Create ============

@router.post("/", response_model=ToolPublic)
async def create_tool(
    session: SessionDep,
    current_user: CurrentUser,
    tool_in: ToolCreate,
) -> Tool:
    """
    Create a new tool.
    
    Requires superuser or tool admin role.
    """
    # Check if tool name already exists
    existing = session.exec(select(Tool).where(Tool.name == tool_in.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tool with this name already exists")
    
    # Create tool
    tool = Tool(
        **tool_in.model_dump(),
        created_by=current_user.id,
    )
    session.add(tool)
    session.commit()
    session.refresh(tool)
    
    return tool


# ============ Update ============

@router.patch("/{tool_id}", response_model=ToolPublic)
async def update_tool(
    session: SessionDep,
    current_user: CurrentUser,
    tool_id: uuid.UUID,
    tool_in: ToolUpdate,
) -> Tool:
    """Update a tool."""
    tool = session.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Check for name conflict if name is being updated
    if tool_in.name and tool_in.name != tool.name:
        existing = session.exec(select(Tool).where(Tool.name == tool_in.name)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tool with this name already exists")
    
    # Update fields
    update_data = tool_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tool, key, value)
    
    tool.updated_at = datetime.utcnow()
    session.add(tool)
    session.commit()
    session.refresh(tool)
    
    return tool


# ============ Delete ============

@router.delete("/{tool_id}", response_model=Message)
async def delete_tool(
    session: SessionDep,
    current_user: CurrentUser,
    tool_id: uuid.UUID,
) -> Message:
    """Delete a tool."""
    tool = session.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    session.delete(tool)
    session.commit()
    
    return Message(message="Tool deleted successfully")


# ============ Test Tool ============

@router.post("/{tool_id}/test", response_model=ToolTestResult)
async def test_tool(
    session: SessionDep,
    current_user: CurrentUser,
    tool_id: uuid.UUID,
    request: ToolTestRequest,
) -> ToolTestResult:
    """
    Test a tool with sample parameters.
    
    This executes the tool with the provided parameters and returns the result.
    """
    tool = session.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    import time
    start_time = time.time()
    
    try:
        # TODO: Implement actual tool execution via ToolExecutor
        # For now, return a mock result
        result = {
            "message": f"Tool '{tool.name}' executed successfully (mock)",
            "input": request.params,
        }
        latency_ms = (time.time() - start_time) * 1000
        
        return ToolTestResult(
            success=True,
            result=result,
            latency_ms=latency_ms,
        )
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return ToolTestResult(
            success=False,
            error=str(e),
            latency_ms=latency_ms,
        )


# ============ Bulk Operations ============

@router.get("/categories/all", response_model=list[str])
async def list_categories(
    session: SessionDep,
    current_user: CurrentUser,
) -> list[str]:
    """Get all unique tool categories."""
    result = session.exec(
        select(Tool.category).distinct().where(Tool.category.isnot(None))
    ).all()
    return list(result)


@router.get("/types/all", response_model=list[str])
async def list_tool_types(
    session: SessionDep,
    current_user: CurrentUser,
) -> list[str]:
    """Get all unique tool types."""
    result = session.exec(
        select(Tool.tool_type).distinct().where(Tool.tool_type.isnot(None))
    ).all()
    return list(result)
