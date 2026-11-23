from dataclasses import dataclass

@dataclass
class ToolResult:
    """
    A result from a tool call.
    """
    tool_name: str
    success: bool
    output: str
    error: str | None = None
    exit_code: int | None = None

    def to_message_content(self) -> str:
        if self.success:
            return self.output

        message = f"Tool execution failed: {self.error}"

        if self.output:
            message += f"\n{self.output}"

        return message