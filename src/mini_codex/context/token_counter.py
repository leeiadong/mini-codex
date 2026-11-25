import json
import math
from typing import Any

from mini_codex.model.messages import Message


class TokenCounter:
    """
    Estimate token usage for model messages and tool schemas.

    This is a heuristic estimator, not an exact model tokenizer.
    """
    CHARS_PER_TOKEN = 2
    MESSAGE_OVERHEAD = 4
    TOOL_CALL_OVERHEAD = 8


    def estimate_text(self, text: str | None) -> int:
        if not text:
            return 0

        return math.ceil(len(text) / self.CHARS_PER_TOKEN)

    def estimate_message(self, message: Message) -> int:
        total = self.MESSAGE_OVERHEAD

        total += self.estimate_text(message.role)
        total += self.estimate_text(message.content)
        total += self.estimate_text(message.tool_call_id)

        for tool_call in message.tool_calls:
            total += self.TOOL_CALL_OVERHEAD
            total += self.estimate_text(tool_call.id)
            total += self.estimate_text(tool_call.name)

            arguments = json.dumps(
                tool_call.arguments,
                ensure_ascii=False,
            )
            total += self.estimate_text(arguments)

        return total

    def estimate_messages(self, messages: list[Message]) -> int:
        return sum(
            self.estimate_message(message)
            for message in messages
        )

    def estimate_tools(self, tools: list[dict[str, Any]]) -> int:
        serialized = json.dumps(
            tools,
            ensure_ascii=False,
        )
        return self.estimate_text(serialized)
