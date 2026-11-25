import json

from mini_codex.context.summary import ContextSummary
from mini_codex.model.client import ModelClient
from mini_codex.model.messages import Message


SUMMARY_SYSTEM_PROMPT = """
You are a context summarizer for a coding agent.

Summarize the supplied conversation into one JSON object.

Rules:
- Use only facts explicitly supported by the conversation.
- Do not invent completed work, test results, file changes, or decisions.
- Preserve the user's original task and explicit constraints.
- Keep unresolved questions and unfinished work in open_questions.
- Record test results as reported, including failures.
- If a field has no supported information, use an empty string or empty list.
- Output valid JSON only. Do not use Markdown fences.

The JSON object must contain exactly these fields:
{
  "task": "string",
  "completed": ["string"],
  "decisions": ["string"],
  "files": ["string"],
  "test_status": "string",
  "open_questions": ["string"],
  "constraints": ["string"]
}
"""


class ContextSummarizer:
    def __init__(self, model: ModelClient):
        self.model = model

    def summarize(
        self,
        messages: list[Message],
        previous_summary: ContextSummary | None = None,
    ) -> ContextSummary:
        conversation = self._serialize_messages(messages)

        previous = (
            previous_summary.to_dict()
            if previous_summary is not None
            else {}
        )

        prompt = {
            "previous_summary": previous,
            "conversation": conversation,
        }

        response = self.model.complete(
            messages=[
                Message(
                    role="system",
                    content=SUMMARY_SYSTEM_PROMPT,
                ),
                Message(
                    role="user",
                    content=json.dumps(prompt, ensure_ascii=False),
                ),
            ],
        )

        if response.tool_calls:
            raise ValueError("Summarizer must not request tool calls")

        if not response.content:
            raise ValueError("Summarizer returned empty content")

        try:
            data = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError("Summarizer returned invalid JSON") from exc

        if not isinstance(data, dict):
            raise ValueError("Summary output must be a JSON object")

        return ContextSummary.from_dict(data)

    def _serialize_messages(
        self,
        messages: list[Message],
    ) -> list[dict]:
        serialized = []

        for message in messages:
            item = {
                "role": message.role,
                "content": message.content,
            }

            if message.tool_calls:
                item["tool_calls"] = [
                    {
                        "id": call.id,
                        "name": call.name,
                        "arguments": call.arguments,
                    }
                    for call in message.tool_calls
                ]

            if message.tool_call_id:
                item["tool_call_id"] = message.tool_call_id

            serialized.append(item)

        return serialized