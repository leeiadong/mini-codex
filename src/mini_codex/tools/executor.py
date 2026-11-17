from pydantic import ValidationError

from mini_codex.model.messages import ToolCall
from mini_codex.tools.registry import ToolRegistry
from mini_codex.tools.result import ToolResult


class ToolExecutor:

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_call: ToolCall) -> ToolResult:

        
        try:
            # 1. 查找工具
            tool = self.registry.get(tool_call.name)

            # 2. 校验参数
            arguments = tool.args_model.model_validate(
                tool_call.arguments
            )

            # 3. 执行工具
            output = tool.function(**arguments.model_dump())

            # 4. 返回成功结果
            return ToolResult(
                tool_name=tool.name,
                success=True,
                output=str(output),
            )
    
        except ValidationError as exc:
            return ToolResult(
                tool_name=tool_call.name,
                success=False,
                output="",
                error=f"Invalid arguments: {exc}",
            )

        except Exception as exc:
            return ToolResult(
                tool_name=tool_call.name,
                success=False,
                output="",
                error=f"{type(exc).__name__}: {exc}",
            )