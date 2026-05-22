from typing import Callable
from dataclasses import dataclass


@dataclass
class Command:
    fn: Callable
    name: str
    description: str


class ExitRepl(Exception):
    pass


REGISTRY: dict[str, Command] = {}


def command(description: str):
    """
    Registers a function as a command via decorator.
    """

    def decorator(fn: Callable) -> Callable:
        REGISTRY[fn.__name__] = Command(
            fn=fn, name=fn.__name__, description=description
        )
        return fn

    return decorator


def dispatch(command_name: str, rest: str = "", **args) -> str:
    if command_name not in REGISTRY:
        return f"Error: unknown command {command_name}"
    command = REGISTRY[command_name]
    try:
        res = command.fn(rest, **args)
        return res if res is not None else ""
    except ExitRepl as e:
        raise
    except Exception as e:
        return f"Error: {command.name} raised {type(e).__name__}: {e}"
