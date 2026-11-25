import pytest

from mini_codex.context.message_pruner import MessagePruner
from mini_codex.context.token_counter import TokenCounter
from mini_codex.model.messages import Message, ToolCall


@pytest.fixture
def pruner():
    return MessagePruner(TokenCounter())


def test_group_normal_messages(pruner):
    messages = [
        Message(role="user", content="Fix the bug"),
        Message(role="assistant", content="I will inspect the code"),
        Message(role="assistant", content="The bug is fixed"),
    ]

    groups = pruner.group_messages(messages)

    assert len(groups) == 3
    assert groups[0] == [messages[0]]
    assert groups[1] == [messages[1]]
    assert groups[2] == [messages[2]]


def test_group_tool_call_and_results(pruner):
    assistant = Message(
        role="assistant",
        content=None,
        tool_calls=[
            ToolCall(id="call_1", name="read_file", arguments={"path": "a.py"}),
            ToolCall(id="call_2", name="read_file", arguments={"path": "b.py"}),
        ],
    )
    result_1 = Message(
        role="tool",
        content="file a",
        tool_call_id="call_1",
    )
    result_2 = Message(
        role="tool",
        content="file b",
        tool_call_id="call_2",
    )

    groups = pruner.group_messages([assistant, result_1, result_2])

    assert len(groups) == 1
    assert groups[0] == [assistant, result_1, result_2]


def test_group_tool_results_can_arrive_in_different_order(pruner):
    assistant = Message(
        role="assistant",
        tool_calls=[
            ToolCall(id="call_1", name="read_file", arguments={}),
            ToolCall(id="call_2", name="read_file", arguments={}),
        ],
    )
    result_2 = Message(role="tool", content="b", tool_call_id="call_2")
    result_1 = Message(role="tool", content="a", tool_call_id="call_1")

    groups = pruner.group_messages([assistant, result_2, result_1])

    assert len(groups) == 1
    assert groups[0] == [assistant, result_2, result_1]


def test_reject_orphan_tool_result(pruner):
    messages = [
        Message(role="tool", content="orphan", tool_call_id="call_1"),
    ]

    with pytest.raises(ValueError, match="Orphan tool result"):
        pruner.group_messages(messages)


def test_reject_incomplete_tool_call_group(pruner):
    messages = [
        Message(
            role="assistant",
            tool_calls=[
                ToolCall(id="call_1", name="read_file", arguments={}),
                ToolCall(id="call_2", name="read_file", arguments={}),
            ],
        ),
        Message(role="tool", content="result", tool_call_id="call_1"),
    ]

    with pytest.raises(ValueError, match="Incomplete tool call group"):
        pruner.group_messages(messages)


def test_prune_preserves_initial_user_message(pruner):
    messages = [
        Message(role="user", content="Fix the project"),
        Message(role="assistant", content="Old analysis"),
        Message(role="assistant", content="Latest answer"),
    ]

    latest_tokens = pruner.token_counter.estimate_message(messages[2])
    budget = pruner.token_counter.estimate_message(messages[0]) + latest_tokens

    result = pruner.prune(messages, budget)

    assert result == [messages[0], messages[2]]


def test_prune_never_splits_tool_call_group(pruner):
    user = Message(role="user", content="Fix the project")
    old_message = Message(role="assistant", content="Old analysis")

    assistant = Message(
        role="assistant",
        tool_calls=[
            ToolCall(id="call_1", name="read_file", arguments={"path": "a.py"}),
            ToolCall(id="call_2", name="read_file", arguments={"path": "b.py"}),
        ],
    )
    result_1 = Message(role="tool", content="A" * 20, tool_call_id="call_1")
    result_2 = Message(role="tool", content="B" * 20, tool_call_id="call_2")

    messages = [user, old_message, assistant, result_1, result_2]

    group_tokens = pruner.token_counter.estimate_messages(
        [assistant, result_1, result_2]
    )
    user_tokens = pruner.token_counter.estimate_message(user)

    result = pruner.prune(messages, user_tokens + group_tokens)

    assert result == [user, assistant, result_1, result_2]


def test_prune_raises_if_initial_request_exceeds_budget(pruner):
    messages = [
        Message(role="user", content="A" * 100),
        Message(role="assistant", content="Answer"),
    ]

    with pytest.raises(ValueError, match="initial user message exceeds"):
        pruner.prune(messages, max_tokens=1)


def test_prune_rejects_negative_budget(pruner):
    with pytest.raises(ValueError, match="non-negative"):
        pruner.prune([], max_tokens=-1)