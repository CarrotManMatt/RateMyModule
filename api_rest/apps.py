"""Application definition & config settings for `api_rest` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("APIRESTAppConfig",)

from django.apps import AppConfig


class APIRESTAppConfig(AppConfig):
    """Config class to hold application's definition & configuration settings."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "api_rest"
    verbose_name = "API REST App"
