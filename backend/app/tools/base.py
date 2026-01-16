from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import json
import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ToolResult(BaseModel):
    """Represents the result of a tool execution."""

    output: Any = Field(default=None)
    error: Optional[str] = Field(default=None)
    base64_image: Optional[str] = Field(default=None)
    system: Optional[str] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __bool__(self):
        return any(getattr(self, field) for field in self.model_fields)

    def __add__(self, other: "ToolResult"):
        def combine_fields(
            field: Optional[str], other_field: Optional[str], concatenate: bool = True
        ):
            if field and other_field:
                if concatenate:
                    return field + other_field
                raise ValueError("Cannot combine tool results")
            return field or other_field

        return ToolResult(
            output=combine_fields(self.output, other.output),
            error=combine_fields(self.error, other.error),
            base64_image=combine_fields(self.base64_image, other.base64_image, False),
            system=combine_fields(self.system, other.system),
        )

    def __str__(self):
        return f"Error: {self.error}" if self.error else str(self.output)

    def replace(self, **kwargs):
        """Returns a new ToolResult with the given fields replaced."""
        return self.model_copy(update=kwargs)


class BaseTool(ABC, BaseModel):
    """Consolidated base class for all tools combining BaseModel and Tool functionality.
    """

    name: str
    description: str
    parameters: Optional[dict] = None

    class Config:
        arbitrary_types_allowed = True

    async def __call__(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        return await self.execute(**kwargs)

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""

    def to_param(self) -> Dict:
        """Convert tool to function call format.

        Returns:
            Dictionary with tool metadata in OpenAI function calling format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def success_response(self, data: Union[Dict[str, Any], str]) -> ToolResult:
        """Create a successful tool result."""
        if isinstance(data, str):
            text = data
        else:
            text = json.dumps(data, indent=2)
        return ToolResult(output=text)

    def fail_response(self, msg: str) -> ToolResult:
        """Create a failed tool result."""
        return ToolResult(error=msg)

class CLIResult(ToolResult):
    """A ToolResult that can be rendered as a CLI output."""

class ToolFailure(ToolResult):
    """A ToolResult that represents a failure."""
