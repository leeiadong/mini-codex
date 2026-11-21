from pathlib import Path

from pydantic import BaseModel, Field

from mini_codex.tools.registry import ToolRegistry
from mini_codex.tools.definition import ToolDefinition

class ReadFileArgs(BaseModel):
    path: str = Field(description="Path to the file to read")


class WriteFileArgs(BaseModel):
    path: str = Field(description="Path to the file to write")
    content: str = Field(description="Content to write to the file")


class FilesystemTools:
    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()

    def _resovel_path(self, path: str) -> Path:
        target = (self.workspace / path).resolve()

        try:
            target.relative_to(self.workspace)
        except ValueError:
            raise ValueError(f"Access denied: path is outside workspace: {path}")

        return target

    def read_file(self, path: str) -> str:
        target = self._resovel_path(path)

        if not target.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not target.is_file():
            raise IsADirectoryError(f"Not a file: {path}")
        
        return target.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str) -> None:
        target = self._resovel_path(path)

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

        return f"Successfully wrote file: {path}"

    def register(self, registry: ToolRegistry) -> None:
        registry.register(
            ToolDefinition(
                name="read_file",
                description="Read a text file inside the workspace",
                args_model=ReadFileArgs,
                function=self.read_file,
            )
        )

        registry.register(
            ToolDefinition(
                name="write_file",
                description="Write content to a file inside the workspace",
                args_model=WriteFileArgs,
                function=self.write_file,
            )
        )
