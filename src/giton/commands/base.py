"""Command bus primitives."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(kw_only=True)
class Command:
    """Base class for every command (intent to change state).

    Subclasses add the parameters of the intent. Commands are values: two
    equal commands must produce the same effect.
    """


CommandHandler = Callable[[Command], Any]


class CommandBus:
    """Routes commands to their single registered handler.

    One handler per command type. Dispatching a command with no registered
    handler raises :class:`KeyError` so wiring mistakes fail loudly.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[Command], CommandHandler] = {}

    def register(self, command_type: type[Command], handler: CommandHandler) -> None:
        self._handlers[command_type] = handler

    def dispatch(self, command: Command) -> Any:
        handler = self._handlers.get(type(command))
        if handler is None:
            raise KeyError(
                f"no command handler registered for {type(command).__name__}"
            )
        return handler(command)

    def handles(self, command_type: type[Command]) -> bool:
        return command_type in self._handlers
