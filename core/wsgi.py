"""
WSGI config for `RateMyModule` project.

It exposes the WSGI callable as a module-level variable named `APPLICATION`.
"""

from collections.abc import Sequence

__all__: Sequence[str] = ("APPLICATION",)

import os

from django.core.handlers.wsgi import WSGIHandler
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

APPLICATION: WSGIHandler = get_wsgi_application()
