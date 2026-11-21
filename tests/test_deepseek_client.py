
import json
from types import SimpleNamespace

from mini_codex.model.deepseek import DeepSeekClient
from mini_codex.model.messages import Message, ToolCall


class FakeCompletions:
    def __init__(self, response):
        self.response = response
        self.request_params = None

    def create(self, **kwargs):
        self.request_params = kwargs
        return self.response


class FakeClient:
    def __init__(self, response):
        self.completions = FakeCompletions(response)
        self.chat = SimpleNamespace(
            completions=self.completions
        )


def test_deepseek_client_text_response():
    api_message = SimpleNamespace(
        content="你好，我是 DeepSeek。",
        tool_calls=None,
    )

    response = SimpleNamespace(
        choices=[
            SimpleNamespace(message=api_message)
        ]
    )

    fake_client = FakeClient(response)

    client = DeepSeekClient(
        model="deepseek-flash",
        client=fake_client,
    )

    result = client.complete(
        [Message(role="user", content="你好")]
    )

    assert result.content == "你好，我是 DeepSeek。"
    assert result.tool_calls == []


def test_deepseek_client_tool_call_response():
    api_tool_call = SimpleNamespace(
        id="call_001",
        function=SimpleNamespace(
            name="calculator",
            arguments='{"a": 123, "b": 456}',
        ),
    )

    api_message = SimpleNamespace(
        content=None,
        tool_calls=[api_tool_call],
    )

    response = SimpleNamespace(
        choices=[
            SimpleNamespace(message=api_message)
        ]
    )

    fake_client = FakeClient(response)

    client = DeepSeekClient(
        model="deepseek-flash",
        client=fake_client,
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Calculate two numbers",
                "parameters": {},
            },
        }
    ]

    result = client.complete(
        [Message(role="user", content="计算 123 + 456")],
        tools=tools,
    )

    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].id == "call_001"
    assert result.tool_calls[0].name == "calculator"
    assert result.tool_calls[0].arguments == {
        "a": 123,
        "b": 456,
    }

    request = fake_client.completions.request_params

    assert request["model"] == "deepseek-flash"
    assert request["tools"] == tools
    assert request["tool_choice"] == "auto"


def test_deepseek_client_serializes_tool_history():
    api_message = SimpleNamespace(
        content="计算完成",
        tool_calls=None,
    )

    response = SimpleNamespace(
        choices=[
            SimpleNamespace(message=api_message)
        ]
    )

    fake_client = FakeClient(response)

    client = DeepSeekClient(client=fake_client)

    messages = [
        Message(
            role="assistant",
            content=None,
            tool_calls=[
                ToolCall(
                    id="call_001",
                    name="calculator",
                    arguments={"a": 123, "b": 456},
                )
            ],
        ),
        Message(
            role="tool",
            content="579",
            tool_call_id="call_001",
        ),
    ]

    client.complete(messages)

    api_messages = fake_client.completions.request_params["messages"]

    assert api_messages[0]["role"] == "assistant"
    assert api_messages[0]["tool_calls"][0]["id"] == "call_001"

    arguments = json.loads(
        api_messages[0]["tool_calls"][0]["function"]["arguments"]
    )
    assert arguments == {"a": 123, "b": 456}

    assert api_messages[1]["role"] == "tool"
    assert api_messages[1]["tool_call_id"] == "call_001"
    assert api_messages[1]["content"] == "579"
