
from pathlib import Path

import pytest

from mini_codex.tools.builtin.shell import ShellExecutor
from mini_codex.tools.registry import ToolRegistry


def test_run_pwd(tmp_path: Path):
    executor = ShellExecutor(tmp_path)

    result = executor.run_command(["pwd"])

    assert result.success is True
    assert result.exit_code == 0
    assert str(tmp_path.resolve()) in result.output


def test_run_python(tmp_path: Path):
    executor = ShellExecutor(tmp_path)

    result = executor.run_command(
        ["python", "--version"]
    )

    assert result.success is True
    assert result.exit_code == 0
    assert "Python" in result.output


def test_reject_unapproved_command(tmp_path: Path):
    executor = ShellExecutor(tmp_path)

    with pytest.raises(ValueError, match="not allowed"):
        executor.run_command(["rm", "-rf", "."])


def test_reject_empty_command(tmp_path: Path):
    executor = ShellExecutor(tmp_path)

    with pytest.raises(ValueError, match="empty"):
        executor.run_command([])


def test_timeout(tmp_path: Path):
    executor = ShellExecutor(tmp_path)

    result = executor.run_command(
        ["python", "-c", "import time; time.sleep(3)"],
        timeout_seconds=1,
    )

    assert "timed out" in result.error
    assert result.success is False
    assert result.exit_code is None


def test_output_truncation(tmp_path: Path):
    executor = ShellExecutor(tmp_path)
    executor.MAX_OUTPUT_CHARS = 100

    result = executor._truncate("A" * 200)

    assert len(result) < 200
    assert "output truncated" in result


def test_register_shell_tool(tmp_path: Path):
    executor = ShellExecutor(tmp_path)
    registry = ToolRegistry()

    executor.register(registry)

    tool = registry.get("run_command")
    assert tool.name == "run_command"

    schemas = registry.get_schemas()
    assert any(
        item["function"]["name"] == "run_command"
        for item in schemas
    )

def test_nonzero_exit_code(tmp_path: Path):
    executor = ShellExecutor(tmp_path)

    result = executor.run_command(
        ["python", "-c", "raise SystemExit(1)"]
    )

    assert result.success is True
    assert result.exit_code == 1


def test_zero_exit_code(tmp_path: Path):
    executor = ShellExecutor(tmp_path)

    result = executor.run_command(
        ["python", "-c", "print('hello')"]
    )

    assert result.success is True
    assert result.exit_code == 0
    assert "hello" in result.output