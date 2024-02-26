#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

from collections.abc import Sequence

__all__: Sequence[str] = ("main",)

import os
import sys
from typing import Final


def main(argv: Sequence[str] | None = None) -> int:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    exc: ImportError
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # noinspection SpellCheckingInspection
        COULDNT_IMPORT_DJANGO_MESSAGE: Final[str] = (
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
        raise ImportError(COULDNT_IMPORT_DJANGO_MESSAGE) from exc

    execute_from_command_line(list(argv) if argv is not None else sys.argv)

    return 0


if __name__ == "__main__":
    main()
