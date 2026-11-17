from typing import Any, Callable 
from mini_codex.model.messages import ToolCall
from mini_codex.tools.definition import ToolDefinition

ToolFunction = Callable[[dict[str, Any]], str]

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name} already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name]

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def get_schemas(self) -> list[dict]:
        return [
            tool.to_schema() for tool in self._tools.values()
        ]