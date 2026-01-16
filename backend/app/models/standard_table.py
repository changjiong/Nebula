
import uuid
from datetime import datetime
from typing import Literal, Optional

from sqlmodel import Column, Field, SQLModel, Relationship
from sqlalchemy.dialects.postgresql import JSONB

# ============ Standard Table ============

class StandardTable(SQLModel, table=True):
    """
    Standard Data Table Definition
    Represents a standardized business data table (e.g., enterprise_info, contract_master).
    """
    __tablename__ = "standard_table"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, unique=True, description="Table identifier (e.g. enterprise_info)")
    display_name: str = Field(max_length=200, description="Human readable name")
    description: Optional[str] = Field(default=None, max_length=2000)
    category: Optional[str] = Field(default="general", max_length=100)
    source: str = Field(
        default="data_warehouse",
        description="Source of this data table: data_warehouse, external_api, ml_output"
    )
    
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    fields: list["TableField"] = Relationship(back_populates="table", sa_relationship_kwargs={"cascade": "all, delete"})
    tool_mappings: list["ToolDataMapping"] = Relationship(back_populates="table")


# ============ Table Field ============

class TableField(SQLModel, table=True):
    """
    Field definition for a StandardTable
    """
    __tablename__ = "table_field"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    table_id: uuid.UUID = Field(foreign_key="standard_table.id", index=True)
    
    name: str = Field(description="Field name (e.g. credit_code)")
    display_name: str = Field(max_length=200)
    data_type: str = Field(default="string", description="string, number, boolean, date, json, array")
    description: Optional[str] = Field(default=None, max_length=1000)
    
    is_primary_key: bool = Field(default=False)
    is_nullable: bool = Field(default=True)
    sample_values: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
        description="Sample values for understanding"
    )

    # Relationships
    table: StandardTable = Relationship(back_populates="fields")
    tool_mappings: list["ToolDataMapping"] = Relationship(back_populates="field")


# ============ Tool Data Mapping ============

class ToolDataMapping(SQLModel, table=True):
    """
    Mapping between Tool parameters (input/output) and StandardTable fields
    This builds the lineage graph.
    """
    __tablename__ = "tool_data_mapping"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    tool_id: uuid.UUID = Field(foreign_key="tool.id", index=True)
    param_path: str = Field(description="JSON path to the parameter (e.g. input.credit_code)")
    param_direction: str = Field(description="input or output")
    
    table_id: uuid.UUID = Field(foreign_key="standard_table.id", index=True)
    field_id: uuid.UUID = Field(foreign_key="table_field.id", index=True)

    # Relationships
    table: StandardTable = Relationship(back_populates="tool_mappings")
    field: TableField = Relationship(back_populates="tool_mappings")
