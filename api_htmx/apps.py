"""Application definition & config settings for `api_htmx` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("APIHTMXAppConfig",)

from django.apps import AppConfig


class APIHTMXAppConfig(AppConfig):
    """Config class to hold application's definition & configuration settings."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "api_htmx"
    verbose_name = "API HTMX App"
