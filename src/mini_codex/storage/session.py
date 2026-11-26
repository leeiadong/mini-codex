from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from dataclasses import asdict

from mini_codex.context.summary import ContextSummary
from mini_codex.model.messages import Message, ToolCall

@dataclass
class Session:
    session_id: str = field(default_factory=lambda: str(uuid4()))
    messages: list[Message] = field(default_factory=list)
    summary: ContextSummary | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_message(self, message: Message) -> None:
        self.messages.append(message)
        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def set_summary(self, summary: ContextSummary) -> None:
        self.summary = summary
        self.touch()

    
    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "name": tool_call.name,
                            "arguments": tool_call.arguments,
                        }
                        for tool_call in (message.tool_calls or [])
                    ],
                }
                for message in self.messages
            ],
            "summary": (
                asdict(self.summary)
                if self.summary is not None
                else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Session":
        messages = []

        for message_data in data["messages"]:
            tool_calls = [
                ToolCall(
                    id=tool_call_data["id"],
                    name=tool_call_data["name"],
                    arguments=tool_call_data["arguments"],
                )
                for tool_call_data in message_data.get("tool_calls", [])
            ]

            messages.append(
                Message(
                    role=message_data["role"],
                    content=message_data["content"],
                    tool_calls=tool_calls,
                )
            )

        summary_data = data.get("summary")

        summary = (
            ContextSummary.from_dict(summary_data)
            if summary_data is not None
            else None
        )

        return cls(
            session_id=data["session_id"],
            messages=messages,
            summary=summary,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )

