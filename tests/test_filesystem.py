
import pytest

from mini_codex.tools.builtin.filesystem import FilesystemTools
from mini_codex.tools.registry import ToolRegistry


def test_read_file(tmp_path):
    (tmp_path / "hello.txt").write_text(
        "Hello Mini-Codex",
        encoding="utf-8",
    )

    fs = FilesystemTools(tmp_path)

    result = fs.read_file("hello.txt")

    assert result == "Hello Mini-Codex"


def test_write_file(tmp_path):
    fs = FilesystemTools(tmp_path)

    result = fs.write_file(
        "src/main.py",
        "print('Hello World')",
    )

    assert result == "Successfully wrote file: src/main.py"
    assert (tmp_path / "src/main.py").read_text(
        encoding="utf-8"
    ) == "print('Hello World')"


def test_read_file_not_found(tmp_path):
    fs = FilesystemTools(tmp_path)

    with pytest.raises(FileNotFoundError):
        fs.read_file("missing.txt")


def test_path_traversal_blocked(tmp_path):
    fs = FilesystemTools(tmp_path)

    with pytest.raises(ValueError, match="outside workspace"):
        fs.read_file("../../etc/passwd")


def test_absolute_path_blocked(tmp_path):
    fs = FilesystemTools(tmp_path)

    with pytest.raises(ValueError, match="outside workspace"):
        fs.read_file("/etc/passwd")


def test_register_filesystem_tools(tmp_path):
    fs = FilesystemTools(tmp_path)
    registry = ToolRegistry()

    fs.register(registry)

    assert registry.get("read_file").name == "read_file"
    assert registry.get("write_file").name == "write_file"

    schemas = registry.get_schemas()

    assert len(schemas) == 2
    assert schemas[0]["function"]["name"] == "read_file"
    assert schemas[1]["function"]["name"] == "write_file"
