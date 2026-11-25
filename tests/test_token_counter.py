
from mini_codex.context.token_counter import TokenCounter
from mini_codex.model.messages import Message, ToolCall


def test_estimate_empty_content():
    counter = TokenCounter()

    message = Message(
        role="user",
        content="",
    )

    result = counter.estimate_message(message)

    assert result > 0


def test_estimate_message_content():
    counter = TokenCounter()

    message = Message(
        role="user",
        content="Hello World",
    )

    result = counter.estimate_message(message)

    assert result == 4 + 2 + 6


def test_estimate_messages():
    counter = TokenCounter()

    messages = [
        Message(role="user", content="Hello"),
        Message(role="assistant", content="World"),
    ]

    result = counter.estimate_messages(messages)

    expected = (
        counter.estimate_message(messages[0])
        + counter.estimate_message(messages[1])
    )

    assert result == expected


def test_estimate_tool_call():
    counter = TokenCounter()

    message = Message(
        role="assistant",
        content=None,
        tool_calls=[
            ToolCall(
                id="call_001",
                name="read_file",
                arguments={"path": "calculator.py"},
            )
        ],
    )

    result = counter.estimate_message(message)

    assert result > counter.MESSAGE_OVERHEAD


def test_estimate_tools():
    counter = TokenCounter()

    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    },
                },
            },
        }
    ]

    result = counter.estimate_tools(tools)

    assert result > 0
