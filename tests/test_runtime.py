from mini_codex.agent.runtime import Agent
from mini_codex.model.messages import (
    Message,
    ModelResponse,
    ToolCall,
)
from mini_codex.tools.registry import ToolRegistry
from pydantic import BaseModel, Field
from mini_codex.tools.definition import ToolDefinition

class CalculatorArgs(BaseModel):
    a: int = Field(description="First number")
    b: int = Field(description="Second number")

class MockModel:

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def complete(self, messages: list[Message], tools: list[dict] | None = None) -> ModelResponse:

        self.calls.append(list(messages))

        return self.responses.pop(0)


def test_agent_tool_call():

    # 1. 模拟模型第一次返回 Tool Call
    first_response = ModelResponse(
        tool_calls=[
            ToolCall(
                id="call_001",
                name="calculator",
                arguments={
                    "a": 123,
                    "b": 456,
                },
            )
        ]
    )

    # 2. 模拟模型第二次返回最终答案
    second_response = ModelResponse(
        content="123 + 456 = 579"
    )

    model = MockModel([
        first_response,
        second_response,
    ])

    # 3. 注册工具
    tools = ToolRegistry()

    def calculator(a: int, b: int) -> str:
        return str(a + b)

    tools.register(
        ToolDefinition(
            name="calculator",
            description="Calculate the sum of two numbers",
            args_model=CalculatorArgs,
            function=calculator,
        )
    )

    # 4. 创建 Agent
    agent = Agent(
        model=model,
        tools=tools,
    )

    # 5. 执行任务
    result = agent.run("计算 123 + 456")

    # 6. 验证结果
    assert result == "123 + 456 = 579"

    # 7. 验证模型被调用两次
    assert len(model.calls) == 2

    # 8. 验证第二次调用包含工具执行结果
    second_call_messages = model.calls[1]

    assert second_call_messages[-1].role == "tool"
    assert second_call_messages[-1].content == "579"
    assert second_call_messages[-1].tool_call_id == "call_001"

def test_agent_preserves_message_history():
    first_response = ModelResponse(
        tool_calls=[
            ToolCall(
                id="call_001",
                name="calculator",
                arguments={"a": 10, "b": 20},
            )
        ]
    )

    second_response = ModelResponse(
        content="结果是 30"
    )

    model = MockModel([
        first_response,
        second_response,
    ])

    tools = ToolRegistry()

    def calculator(a: int, b: int) -> str:
        return str(a + b)

    tools.register(
        ToolDefinition(
            name="calculator",
            description="Calculate the sum of two numbers",
            args_model=CalculatorArgs,
            function=calculator,
        )
    )

    agent = Agent(model=model, tools=tools)

    result = agent.run("计算 10 + 20")

    assert result == "结果是 30"

    # 第二次调用应该包含完整历史
    messages = model.calls[1]

    assert len(messages) == 3

    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert messages[2].role == "tool"

    assert messages[2].content == "30"