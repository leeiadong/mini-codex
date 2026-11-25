from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass
class ContextSummary:
    task: str = ""
    completed: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    test_status: str = ""
    open_questions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContextSummary":
        expected_fields = {
            "task",
            "completed",
            "decisions",
            "files",
            "test_status",
            "open_questions",
            "constraints",
        }

        # print("Actual fields:", sorted(data.keys()))
        # print("Expected fields:", sorted(expected_fields))
        # print("Missing fields:", sorted(expected_fields - set(data)))
        # print("Unexpected fields:", sorted(set(data) - expected_fields))

        if set(data) != expected_fields:
            raise ValueError(
                "Summary must contain exactly these fields: "
                + ", ".join(sorted(expected_fields))
            )

        for field_name in ("task", "test_status"):
            if not isinstance(data[field_name], str):
                raise ValueError(f"{field_name} must be a string")

        list_fields = [
            "completed",
            "decisions",
            "files",
            "open_questions",
            "constraints",
        ]

        for field_name in list_fields:
            value = data[field_name]

            if not isinstance(value, list):
                raise ValueError(f"{field_name} must be a list")

            if not all(isinstance(item, str) for item in value):
                raise ValueError(f"Every item in {field_name} must be a string")

        return cls(**data)

    def to_message_content(self) -> str:
        """
        Serialize the summary for inclusion in model context.
        """
        import json

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=2,
        )