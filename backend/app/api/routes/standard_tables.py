
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep, CurrentUser
from app.models import (
    StandardTable,
    TableField,
    TableFieldCreate,
    TableFieldUpdate,
    ToolDataMapping,
    ToolDataMappingCreate,
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


# ============ Table Field CRUD ============

@router.post("/standard-tables/fields", response_model=TableField)
def create_table_field(
    field_in: TableFieldCreate,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Add a field to a standard table.
    """
    table = session.get(StandardTable, field_in.table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Standard table not found")
        
    field = TableField.model_validate(field_in)
    session.add(field)
    session.commit()
    session.refresh(field)
    return field


@router.put("/standard-tables/fields/{id}", response_model=TableField)
def update_table_field(
    id: uuid.UUID,
    field_in: TableFieldUpdate,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Update a standard table field.
    """
    field = session.get(TableField, id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
        
    field_data = field_in.model_dump(exclude_unset=True)
    field.sqlmodel_update(field_data)
    
    session.add(field)
    session.commit()
    session.refresh(field)
    return field


@router.delete("/standard-tables/fields/{id}")
def delete_table_field(
    id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Delete a standard table field.
    """
    field = session.get(TableField, id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
        
    session.delete(field)
    session.commit()
    return {"ok": True}


# ============ Tool Data Mapping CRUD ============

@router.post("/tools/mappings", response_model=ToolDataMapping)
def create_tool_mapping(
    mapping_in: ToolDataMappingCreate,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Create a mapping between tool parameter and standard table field.
    """
    # Verify references
    if not session.get(Tool, mapping_in.tool_id):
        raise HTTPException(status_code=404, detail="Tool not found")
    if not session.get(StandardTable, mapping_in.table_id):
        raise HTTPException(status_code=404, detail="Standard table not found")
    if not session.get(TableField, mapping_in.field_id):
        raise HTTPException(status_code=404, detail="Table field not found")
        
    mapping = ToolDataMapping.model_validate(mapping_in)
    session.add(mapping)
    session.commit()
    session.refresh(mapping)
    return mapping


@router.delete("/tools/mappings/{id}")
def delete_tool_mapping(
    id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Delete a tool data mapping.
    """
    mapping = session.get(ToolDataMapping, id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
        
    session.delete(mapping)
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
