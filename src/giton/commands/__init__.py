"""Command side of giton's CQRS split.

A *command* is an intent to change state (install a plugin, save findings,
apply a fix). Commands are dispatched through the :class:`CommandBus` to a
single registered handler. Handlers perform the work and — where it represents
a domain fact — publish an :mod:`~giton.events` event.

Per bounded-context commands live in :mod:`giton.commands.plugins` and
:mod:`giton.commands.policy`.
"""
from giton.commands.base import Command, CommandBus, CommandHandler

__all__ = ["Command", "CommandBus", "CommandHandler"]
