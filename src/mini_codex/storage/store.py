from typing import Protocol, runtime_checkable

from mini_codex.storage.session import Session

@runtime_checkable
class SessionStore(Protocol):
    def save(self, session: Session) -> None:
        """保存或更新一个 Session。"""
        ...

    def get(self, session_id: str) -> Session | None:
        """读取 Session；不存在时返回 None。"""
        ...

    def delete(self, session_id: str) -> bool:
        """删除 Session；存在并删除时返回 True，否则返回 False。"""
        ...