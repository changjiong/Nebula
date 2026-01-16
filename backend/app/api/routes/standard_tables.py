
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep, CurrentUser
from app.models import (
    StandardTable,
    TableField,
    ToolDataMapping,
    Tool
)
from app.models.standard_table import StandardTable

router = APIRouter()

# ============ Standard Table CRUD ============

@router.get("/standard-tables", response_model=dict)
def list_standard_tables(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    source: str | None = None
) -> Any:
    """
    List standard data tables.
    """
    query = select(StandardTable)
    if source:
        query = query.where(StandardTable.source == source)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_count = session.exec(count_query).one()
    
    query = query.offset(skip).limit(limit)
    tables = session.exec(query).all()
    
    return {"data": tables, "count": total_count}


@router.get("/standard-tables/{id}", response_model=StandardTable)
def get_standard_table(
    id: uuid.UUID,
    session: SessionDep
) -> Any:
    """
    Get standard table details including fields.
    """
    table = session.get(StandardTable, id)
    if not table:
        raise HTTPException(status_code=404, detail="Standard table not found")
    return table


@router.post("/standard-tables", response_model=StandardTable)
def create_standard_table(
    table_in: StandardTable,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Create a new standard data table.
    """
    # Check uniqueness
    existing = session.exec(
        select(StandardTable).where(StandardTable.name == table_in.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Table name already exists")
        
    session.add(table_in)
    session.commit()
    session.refresh(table_in)
    return table_in


@router.put("/standard-tables/{id}", response_model=StandardTable)
def update_standard_table(
    id: uuid.UUID,
    table_in: StandardTable,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Update a standard data table.
    """
    table = session.get(StandardTable, id)
    if not table:
        raise HTTPException(status_code=404, detail="Standard table not found")
        
    table_data = table_in.model_dump(exclude_unset=True)
    table.sqlmodel_update(table_data)
    
    session.add(table)
    session.commit()
    session.refresh(table)
    return table


@router.delete("/standard-tables/{id}")
def delete_standard_table(
    id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Delete a standard data table.
    """
    table = session.get(StandardTable, id)
    if not table:
        raise HTTPException(status_code=404, detail="Standard table not found")
        
    session.delete(table)
    session.commit()
    return {"ok": True}


# ============ Tool Data Graph ============

@router.get("/tools/{tool_id}/data-graph", response_model=dict)
def get_tool_data_graph(
    tool_id: uuid.UUID,
    session: SessionDep
) -> Any:
    """
    Get the data lineage graph for a tool.
    Returns:
    {
        "tool": Tool,
        "input_mappings": [ToolDataMapping],
        "output_mappings": [ToolDataMapping],
        "tables": [StandardTable]  # Associated tables
    }
    """
    tool = session.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
        
    mappings = session.exec(
        select(ToolDataMapping).where(ToolDataMapping.tool_id == tool_id)
    ).all()
    
    # Collect unique table IDs
    table_ids = {m.table_id for m in mappings}
    tables = session.exec(
        select(StandardTable).where(StandardTable.id.in_(table_ids))
    ).all()
    
    return {
        "tool": tool,
        "mappings": mappings,
        "tables": tables
    }
