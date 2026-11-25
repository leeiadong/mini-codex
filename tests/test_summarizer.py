import json

import pytest

from mini_codex.context.summarizer import ContextSummarizer
from mini_codex.context.summary import ContextSummary
from mini_codex.model.messages import Message, ModelResponse, ToolCall


class MockModel:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def complete(self, messages, tools=None):
        self.calls.append(messages)
        return self.response


def make_summary_json():
    return json.dumps(
        {
            "task": "Fix the project",
            "completed": ["Fixed calculator.add"],
            "decisions": ["Keep tool call groups atomic"],
            "files": ["calculator.py"],
            "test_status": "8 passed",
            "open_questions": [],
            "constraints": ["Do not modify tests"],
        }
    )


def test_summarizer_returns_structured_summary():
    model = MockModel(
        ModelResponse(content=make_summary_json())
    )
    summarizer = ContextSummarizer(model)

    result = summarizer.summarize(
        [Message(role="user", content="Fix the project")]
    )

    assert isinstance(result, ContextSummary)
    assert result.task == "Fix the project"
    assert result.completed == ["Fixed calculator.add"]


def test_summarizer_sends_conversation_to_model():
    model = MockModel(
        ModelResponse(content=make_summary_json())
    )
    summarizer = ContextSummarizer(model)

    summarizer.summarize(
        [Message(role="user", content="Fix the project")]
    )

    sent_messages = model.calls[0]

    assert sent_messages[0].role == "system"
    assert sent_messages[1].role == "user"
    assert "Fix the project" in sent_messages[1].content


def test_summarizer_includes_previous_summary():
    model = MockModel(
        ModelResponse(content=make_summary_json())
    )
    summarizer = ContextSummarizer(model)

    previous = ContextSummary(
        task="Fix the project",
        completed=["Fixed calculator.add"],
    )

    summarizer.summarize(
        [Message(role="assistant", content="Fixed validator.py")],
        previous_summary=previous,
    )

    prompt = model.calls[0][1].content
    data = json.loads(prompt)

    assert data["previous_summary"]["completed"] == [
        "Fixed calculator.add"
    ]


def test_summarizer_rejects_invalid_json():
    model = MockModel(ModelResponse(content="not json"))
    summarizer = ContextSummarizer(model)

    with pytest.raises(ValueError, match="invalid JSON"):
        summarizer.summarize([])


def test_summarizer_rejects_incomplete_summary():
    model = MockModel(
        ModelResponse(content=json.dumps({"task": "Fix the project"}))
    )
    summarizer = ContextSummarizer(model)

    with pytest.raises(ValueError, match="exactly these fields"):
        summarizer.summarize([])


def test_summarizer_rejects_tool_calls():
    model = MockModel(
        ModelResponse(
            content=make_summary_json(),
            tool_calls=[
                ToolCall(
                    id="call_1",
                    name="read_file",
                    arguments={"path": "calculator.py"},
                )
            ],
        )
    )
    summarizer = ContextSummarizer(model)

    with pytest.raises(ValueError, match="must not request tool calls"):
        summarizer.summarize([])