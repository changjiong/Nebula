import os
from pathlib import Path
from typing import Literal, Optional, List
from pydantic import Field

from app.tools.base import BaseTool, ToolResult

Command = Literal["read_file", "write_file", "list_directory"]

class FileTool(BaseTool):
    """
    A tool for file system operations: reading files, writing files, and listing directories.
    Safe for use with local paths.
    """
    name: str = "file_tool"
    description: str = """
    Perform file operations on the local filesystem.
    Supported commands:
    - read_file: Read the contents of a file.
    - write_file: Create or overwrite a file with transparency.
    - list_directory: List contents of a directory.
    """
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "enum": ["read_file", "write_file", "list_directory"],
                "description": "The command to execute.",
            },
            "path": {
                "type": "string",
                "description": "The absolute path to the file or directory.",
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file. Required for 'write_file'.",
            }
        },
        "required": ["command", "path"],
    }

    async def execute(
        self,
        command: Command,
        path: str,
        content: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        try:
            target_path = Path(path)
            
            # basic security check: ensure path is absolute
            if not target_path.is_absolute():
                 return self.fail_response(f"Path must be absolute: {path}")

            if command == "read_file":
                return await self._read_file(target_path)
            elif command == "write_file":
                if content is None:
                    return self.fail_response("Parameter 'content' is required for write_file")
                return await self._write_file(target_path, content)
            elif command == "list_directory":
                return await self._list_directory(target_path)
            else:
                return self.fail_response(f"Unknown command: {command}")

        except Exception as e:
            return self.fail_response(f"Error executing {command}: {str(e)}")

    async def _read_file(self, path: Path) -> ToolResult:
        if not path.exists():
            return self.fail_response(f"File not found: {path}")
        if not path.is_file():
             return self.fail_response(f"Path is not a file: {path}")
        
        try:
            content = path.read_text(encoding='utf-8')
            return self.success_response(content)
        except Exception as e:
            return self.fail_response(f"Failed to read file: {e}")

    async def _write_file(self, path: Path, content: str) -> ToolResult:
        try:
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            return self.success_response(f"Successfully wrote to {path}")
        except Exception as e:
             return self.fail_response(f"Failed to write file: {e}")

    async def _list_directory(self, path: Path) -> ToolResult:
        if not path.exists():
             return self.fail_response(f"Directory not found: {path}")
        if not path.is_dir():
             return self.fail_response(f"Path is not a directory: {path}")
        
        try:
            items = []
            for item in path.iterdir():
                type_str = "DIR" if item.is_dir() else "FILE"
                items.append(f"{type_str:4} {item.name}")
            
            output = "\n".join(sorted(items))
            return self.success_response(output if output else "(empty directory)")
        except Exception as e:
            return self.fail_response(f"Failed to list directory: {e}")
