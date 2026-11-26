from dataclasses import dataclass
from typing import Any

from mini_codex.context.token_counter import TokenCounter
from mini_codex.context.message_pruner import MessagePruner
from mini_codex.context.summary import ContextSummary
from mini_codex.context.summarizer import ContextSummarizer
from mini_codex.model.messages import Message


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
        summarizer: ContextSummarizer | None = None,
        pruner: MessagePruner | None = None,
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
        self.summarizer = summarizer
        self.pruner = pruner or MessagePruner(self.token_counter)

    def prepare(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        system_prompt: str | None = None,
        previous_summary: ContextSummary | None = None,
    ) -> list[Message]:
        if not messages:
            return []

        budget = self.calculate_budget(
            tools=tools,
            system_prompt=system_prompt,
        )

        message_tokens = self.token_counter.estimate_messages(messages)

        # The history already fits: do not call the summarization model.
        if message_tokens <= budget.message_tokens:
            return messages

        if self.summarizer is None:
            raise ValueError(
                "Conversation exceeds the context budget and no summarizer is configured"
            )

        summary = self.summarizer.summarize(
            messages,
            previous_summary=previous_summary,
        )

        summary_message = Message(
            role="system",
            content=summary.to_message_content(),
        )

        # Put the summary before the initial user task so the pruner
        # preserves both the summary and the original task.
        pinned_system_count = 0
        while (
            pinned_system_count < len(messages)
            and messages[pinned_system_count].role == "system"
        ):
            pinned_system_count += 1

        prepared = [
            *messages[:pinned_system_count],
            summary_message,
            *messages[pinned_system_count:],
        ]

        summary_tokens = self.token_counter.estimate_messages(
            [summary_message]
        )

        remaining_budget = budget.message_tokens - summary_tokens

        if remaining_budget <= 0:
            raise ValueError(
                "Context summary exceeds the available message budget"
            )

        return self.pruner.prune(
            prepared,
            max_tokens=budget.message_tokens,
        )

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