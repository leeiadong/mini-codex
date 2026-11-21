
import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from mini_codex.model.messages import Message, ModelResponse, ToolCall


class DeepSeekClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        client: Any | None = None,
    ):
        load_dotenv()

        self.model = model or os.getenv(
            "DEEPSEEK_MODEL",
            "deepseek-flash",
        )

        if client is not None:
            # 允许注入 Mock Client，方便单元测试
            self.client = client
        else:
            resolved_api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

            if not resolved_api_key:
                raise ValueError(
                    "Missing DEEPSEEK_API_KEY. "
                    "Please configure it in your .env file."
                )

            self.client = OpenAI(
                api_key=resolved_api_key,
                base_url=(
                    base_url
                    or os.getenv(
                        "DEEPSEEK_BASE_URL",
                        "https://api.deepseek.com",
                    )
                ),
            )

    def complete(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> ModelResponse:
        api_messages = self._serialize_messages(messages)

        request_params = {
            "model": self.model,
            "messages": api_messages,
            "extra_body": {
                "thinking": {"type": "disabled"}
            },
        }

        if tools:
            request_params["tools"] = tools
            request_params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(
            **request_params
        )

        return self._parse_response(response)

    def _serialize_messages(
        self,
        messages: list[Message],
    ) -> list[dict]:
        """Convert internal messages to OpenAI-compatible format."""
        result = []

        for message in messages:
            item = {
                "role": message.role,
                "content": message.content,
            }

            if message.tool_calls:
                item["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": json.dumps(
                                tool_call.arguments,
                                ensure_ascii=False,
                            ),
                        },
                    }
                    for tool_call in message.tool_calls
                ]

            if message.tool_call_id:
                item["tool_call_id"] = message.tool_call_id

            result.append(item)

        return result

    def _parse_response(self, response: Any) -> ModelResponse:
        """Convert API response to internal ModelResponse."""
        if not response.choices:
            raise ValueError("DeepSeek returned no choices")

        api_message = response.choices[0].message

        tool_calls = []

        for item in api_message.tool_calls or []:
            arguments = json.loads(item.function.arguments or "{}")

            if not isinstance(arguments, dict):
                raise ValueError(
                    f"Tool arguments must be a JSON object: {item.function.name}"
                )

            tool_calls.append(
                ToolCall(
                    id=item.id,
                    name=item.function.name,
                    arguments=arguments,
                )
            )

        return ModelResponse(
            content=api_message.content,
            tool_calls=tool_calls,
        )
