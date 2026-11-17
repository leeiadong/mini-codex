from typing import Any, Callable 
from mini_codex.model.messages import ToolCall

ToolFunction = Callable[[dict[str, Any]], str]

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolFunction] = {}

    def register(
            self,
            name: str,
            func: ToolFunction,
    ) -> None:
        self._tools[name] = func

    def execute(self, tool_call: ToolCall) -> str:
        if tool_call.name not in self._tools:
            raise ValueError(f"Unknown tool: {tool_call.name}")
        tool = self._tools[tool_call.name]
        return tool(tool_call.arguments)