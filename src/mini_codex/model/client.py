from typing import Protocol

from mini_codex.model.messages import Message, ModelResponse


class ModelClient(Protocol):

    """
    只要某个类实现了 complete() 方法，并且符合对应的输入输出类型，就可以作为 ModelClient 使用
    依赖抽象而不是依赖具体实现
    """
    def complete(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> ModelResponse:
        ...