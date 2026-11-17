from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel


@dataclass
class ToolDefinition:
    name: str
    description: str
    args_model: type[BaseModel]
    function: Callable[..., Any]

    def to_schema(self) -> dict:
        """Convert tool definition to OpenAI-compatible schema."""

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_model.model_json_schema(),
            },
        }



from pydantic import BaseModel, Field


class CalculatorArgs(BaseModel):
    a: float = Field(description="First number")
    b: float = Field(description="Second number")