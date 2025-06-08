"""Example configuration definitions for testing."""
from __future__ import annotations


def configclass(cls=None):
    """Return the decorated class unmodified."""
    def wrap(c):
        return c
    if cls is None:
        return wrap
    return wrap(cls)


def config_field(**kwargs):
    """Return passed kwargs for inspection."""
    return kwargs


@configclass
class MyConfig:
    """Example configuration class."""

    name: str = config_field(default="demo")
    level: int = config_field(default=1)

