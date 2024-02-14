"""Handles signals sent within the `ratemymodule` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("ready",)


def ready() -> None:
    """Initialise this module when importing & starting signal listeners."""
