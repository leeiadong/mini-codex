
import pytest

from pydantic import BaseModel, Field

from mini_codex.model.messages import ToolCall
from mini_codex.tools.definition import ToolDefinition
from mini_codex.tools.registry import ToolRegistry
from mini_codex.tools.executor import ToolExecutor


class CalculatorArgs(BaseModel):
    a: float = Field(description="First number")
    b: float = Field(description="Second number")


def calculator(a: float, b: float) -> float:
    return a + b


def create_registry():
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="calculator",
            description="Calculate the sum of two numbers",
            args_model=CalculatorArgs,
            function=calculator,
        )
    )

    return registry


def test_tool_registration():
    registry = create_registry()

    assert len(registry.list_tools()) == 1
    assert registry.get("calculator").name == "calculator"


def test_duplicate_tool_registration():
    registry = create_registry()

    with pytest.raises(ValueError):
        registry.register(registry.get("calculator"))


def test_tool_schema_generation():
    registry = create_registry()

    schemas = registry.get_schemas()

    assert len(schemas) == 1
    assert schemas[0]["type"] == "function"
    assert schemas[0]["function"]["name"] == "calculator"

    parameters = schemas[0]["function"]["parameters"]

    assert "a" in parameters["properties"]
    assert "b" in parameters["properties"]


def test_tool_execution_success():
    executor = ToolExecutor(create_registry())

    result = executor.execute(
        ToolCall(
            id="call_001",
            name="calculator",
            arguments={"a": 123, "b": 456},
        )
    )

    assert result.success is True
    assert result.output == "579.0"
    assert result.error is None


def test_tool_execution_invalid_arguments():
    executor = ToolExecutor(create_registry())

    result = executor.execute(
        ToolCall(
            id="call_002",
            name="calculator",
            arguments={"a": 123},
        )
    )

    assert result.success is False
    assert "Invalid arguments" in result.error


def test_tool_execution_unknown_tool():
    executor = ToolExecutor(create_registry())

    result = executor.execute(
        ToolCall(
            id="call_003",
            name="unknown_tool",
            arguments={},
        )
    )

    assert result.success is False
    assert "Unknown tool" in result.error
