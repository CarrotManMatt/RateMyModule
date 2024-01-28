"""Application definition & config settings for `web` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("WebServerConfig",)

from django.apps import AppConfig


class WebServerConfig(AppConfig):
    """Config class to hold application's definition & configuration settings."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "web"
    verbose_name = "Web Server App"
