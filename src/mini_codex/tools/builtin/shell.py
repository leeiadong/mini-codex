import shutil
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from mini_codex.tools.definition import ToolDefinition
from mini_codex.tools.registry import ToolRegistry
from mini_codex.tools.result import ToolResult

class RunCommandArgs(BaseModel):
    argv: list[str] = Field(
        min_length=1,
        description="Command and arguments, for example ['pytest', '-q']",
    )

    timeout_seconds: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Maximum command execution time in seconds",
    )


class ShellExecutor:
    ALLOWED_COMMANDS = {
        "pwd",
        "ls",
        "python",
        "python3",
        "pytest",
    }

    MAX_OUTPUT_CHARS = 10_000

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()

    def run_command(
        self,
        argv: list[str],
        timeout_seconds: int = 10,
    ) -> str:
        if not argv or not argv[0]:
            raise ValueError("Command cannot be empty")

        command = argv[0]

        # Only allow explicitly approved executable names.
        if command not in self.ALLOWED_COMMANDS:
            raise ValueError(f"Command is not allowed: {command}")

        # Reject NUL bytes before passing arguments to the OS.
        if any("\x00" in arg for arg in argv):
            raise ValueError("Command arguments cannot contain NUL bytes")

        executable = shutil.which(command)
        if executable is None:
            raise FileNotFoundError(
                f"Executable not found: {command}"
            )

        try:
            completed = subprocess.run(
                [executable, *argv[1:]],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                shell=False,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = self._decode_output(exc.stdout)
            stderr = self._decode_output(exc.stderr)

            output = (
                f"Command timed out after {timeout_seconds} seconds.\n"
                f"stdout:\n{stdout}\n"
                f"stderr:\n{stderr}"
            )
            return ToolResult(
                tool_name="run_command",
                success=False,
                output=self._truncate(
                    f"stdout:\n{stdout}\nstderr:\n{stderr}"
                ),
                error=f"Command timed out after {timeout_seconds} seconds",
            )

        output = (
            f"Exit code: {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

        return ToolResult(
            tool_name="run_command",
            success=True,
            output=self._truncate(output),
            exit_code=completed.returncode,
        )

    def _decode_output(self, value: str | bytes | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value

    def _truncate(self, output: str) -> str:
        if len(output) <= self.MAX_OUTPUT_CHARS:
            return output

        return (
            output[: self.MAX_OUTPUT_CHARS]
            + "\n... output truncated ..."
        )

    def register(self, registry: ToolRegistry) -> None:
        registry.register(
            ToolDefinition(
                name="run_command",
                description=(
                    "Run an approved command inside the workspace. "
                    "Use argv as a list, not a shell command string."
                ),
                args_model=RunCommandArgs,
                function=self.run_command,
            )
        )
