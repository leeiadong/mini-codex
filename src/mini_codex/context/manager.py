from dataclasses import dataclass
from typing import Any

from mini_codex.context.token_counter import TokenCounter


@dataclass(frozen=True)
class ContextBudget:
    max_context_tokens: int
    reserved_output_tokens: int
    tool_tokens: int
    system_tokens: int
    message_tokens: int


class ContextManager:
    def __init__(
        self,
        max_context_tokens: int,
        reserved_output_tokens: int,
        token_counter: TokenCounter | None = None,
    ) -> None:
        if max_context_tokens <= 0:
            raise ValueError("max_context_tokens must be greater than 0")

        if reserved_output_tokens < 0:
            raise ValueError("reserved_output_tokens cannot be negative")

        if reserved_output_tokens >= max_context_tokens:
            raise ValueError(
                "reserved_output_tokens must be smaller than max_context_tokens"
            )

        self.max_context_tokens = max_context_tokens
        self.reserved_output_tokens = reserved_output_tokens
        self.token_counter = token_counter or TokenCounter()

    def calculate_budget(
        self,
        tools: list[dict[str, Any]] | None = None,
        system_prompt: str | None = None,
    ) -> ContextBudget:
        tools = tools or []
        system_prompt = system_prompt or ""

        tool_tokens = self.token_counter.estimate_tools(tools)
        system_tokens = self.token_counter.estimate_text(system_prompt)

        message_tokens = (
            self.max_context_tokens
            - self.reserved_output_tokens
            - tool_tokens
            - system_tokens
        )

        if message_tokens <= 0:
            raise ValueError(
                "No token budget remains for conversation messages: "
                f"context={self.max_context_tokens}, "
                f"output={self.reserved_output_tokens}, "
                f"tools={tool_tokens}, "
                f"system={system_tokens}"
            )

        return ContextBudget(
            max_context_tokens=self.max_context_tokens,
            reserved_output_tokens=self.reserved_output_tokens,
            tool_tokens=tool_tokens,
            system_tokens=system_tokens,
            message_tokens=message_tokens,
        )