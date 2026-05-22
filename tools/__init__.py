from dataclasses import dataclass
from typing import Callable
import json
from pydantic import BaseModel
from openai.types.chat import ChatCompletionFunctionToolParam


@dataclass
class ToolEntry:
    fn: Callable
    input_model: type[BaseModel]
    name: str
    description: str


REGISTRY: dict[str, ToolEntry] = {}


def tool(input_model: type[BaseModel], description: str):
    """Decorator: register a function as a tool the model can call."""

    def decorator(fn: Callable) -> Callable:
        REGISTRY[fn.__name__] = ToolEntry(
            fn=fn,
            input_model=input_model,
            name=fn.__name__,
            description=description,
        )
        return fn

    return decorator


def get_schemas() -> list[ChatCompletionFunctionToolParam]:
    """Convert registry → OpenAI-style tool schemas for the API call."""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.input_model.model_json_schema(),
            },
        }
        for t in REGISTRY.values()
    ]


def dispatch(name: str, raw_args: str, **context) -> str:
    """Execute a tool call. `context` carries store, model, config, etc."""
    if name not in REGISTRY:
        return f"Error: unknown tool '{name}'"
    entry = REGISTRY[name]
    try:
        args = json.loads(raw_args or "{}")
        validated = entry.input_model(**args)
    except Exception as e:
        return f"Error: invalid arguments for {name}: {e}"
    try:
        return str(entry.fn(validated, **context))
    except Exception as e:
        return f"Error: {name} raised {type(e).__name__}: {e}"
