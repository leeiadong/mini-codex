import pytest

from mini_codex.context.summary import ContextSummary


def test_summary_defaults():
    summary = ContextSummary()

    assert summary.task == ""
    assert summary.completed == []
    assert summary.open_questions == []


def test_summary_to_dict_and_back():
    summary = ContextSummary(
        task="Fix the project",
        completed=["Fixed calculator.add"],
        decisions=["Keep tool call groups atomic"],
        files=["calculator.py"],
        test_status="8 passed",
        open_questions=["Review validator edge cases"],
        constraints=["Do not modify tests"],
    )

    restored = ContextSummary.from_dict(summary.to_dict())

    assert restored == summary


def test_summary_to_message_content_is_json():
    summary = ContextSummary(
        task="修复项目",
        completed=["修复 calculator.add"],
    )

    content = summary.to_message_content()

    assert "修复项目" in content
    assert "calculator.add" in content


def test_summary_rejects_missing_fields():
    with pytest.raises(ValueError, match="exactly these fields"):
        ContextSummary.from_dict({
            "task": "Fix the project",
        })


def test_summary_rejects_wrong_field_type():
    data = ContextSummary().to_dict()
    data["completed"] = "Fixed calculator.add"

    with pytest.raises(ValueError, match="completed must be a list"):
        ContextSummary.from_dict(data)


def test_summary_rejects_non_string_list_items():
    data = ContextSummary().to_dict()
    data["completed"] = ["Fixed calculator.add", 123]

    with pytest.raises(ValueError, match="Every item"):
        ContextSummary.from_dict(data)