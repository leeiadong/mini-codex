import json, redis
from mini_codex.storage.session import Session

class RedisStorage:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        ttl: int | None = 86400,
        key_prefix: str = "mini_codex:session",
    ):
        if ttl is not None and ttl <= 0:
            raise ValueError("ttl must be greater than 0")

        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
        )
        self.ttl = ttl
        self.key_prefix = key_prefix

    def _make_key(self, session_id: str) -> str:
        return f"{self.key_prefix}:{session_id}"

    def save(self, session: Session) -> None:
        key = self._make_key(session.session_id)
        value = json.dumps(session.to_dict(),ensure_ascii=False,)

        if self.ttl is None:
            self.client.set(key, value)
        else:
            self.client.set(key, value, ex=self.ttl)

    def get(self, session_id: str) -> Session | None:
        key = self._make_key(session_id)
        value = self.client.get(key)
        if value is None:
            return None
        return Session.from_dict(json.loads(value))

    def delete(self, session_id: str) -> bool:
        key = self._make_key(session_id)
        return bool(self.client.delete(key))

    def close(self) -> None:
        self.client.close()

    def ping(self) -> bool:
        return bool(self.client.ping())
