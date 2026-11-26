from mini_codex.model.client import ModelClient
from mini_codex.model.messages import Message
from mini_codex.tools.registry import ToolRegistry
from mini_codex.tools.executor import ToolExecutor
from mini_codex.context.manager import ContextManager

import logging

logger = logging.getLogger(__name__)


class Agent:

    def __init__(
        self,
        model: ModelClient,
        tools: ToolRegistry,
        max_steps: int = 10,
        context_manager: ContextManager | None = None,
    ):
        self.model = model
        self.tools = tools
        self.max_steps = max_steps
        self.tool_executor = ToolExecutor(tools)
        self.context_manager = context_manager

    def run(self, user_input: str) -> str:

        # 1. 初始化消息
        messages = [
            Message(
                role="user",
                content=user_input,
            )
        ]

        # 2. Agent Loop
        for step in range(self.max_steps):

            logger.info(
                "Step %d/%d: Calling model",
                step + 1,
                self.max_steps,
            )

            # 3. 调用模型
            # response = self.model.complete(messages, tools=self.tools.get_schemas())
            tool_schemas = self.tools.get_schemas()
            if self.context_manager is not None:
                prepared_messages = self.context_manager.prepare(
                    messages=messages,
                    tools=tool_schemas,
                )
            else:
                prepared_messages = messages

            response = self.model.complete(
                prepared_messages,
                tools=tool_schemas,
            )

            logger.info(
                "Model returned %d tool call(s)",
                len(response.tool_calls),
            )

            # 4. 保存 Assistant Message
            assistant_message = Message(
                role="assistant",
                content=response.content,
                tool_calls=response.tool_calls,
            )

            messages.append(assistant_message)

            # 5. 没有 Tool Call，说明模型已经完成任务
            if not response.tool_calls:
                logger.info("Agent task completed")
                return response.content or ""

            # 6. 执行所有 Tool Calls
            for tool_call in response.tool_calls:

                logger.info(
                    "Executing tool: %s (call_id=%s)",
                    tool_call.name,
                    tool_call.id,
                )

                result = self.tool_executor.execute(tool_call)

                logger.info(
                    "Tool finished: name=%s, success=%s, exit_code=%s, output_chars=%d",
                    result.tool_name,
                    result.success,
                    result.exit_code,
                    len(result.output),
                )

                # 7. 把工具结果加入上下文
                messages.append(
                    Message(
                        role="tool",
                        content=result.to_message_content(),
                        tool_call_id=tool_call.id,
                    )
                )

        # 8. 超过最大执行步数
        raise RuntimeError(
            f"Agent exceeded maximum steps: {self.max_steps}"
        )