"""Application definition & config settings for `ratemymodule` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("RateMyModuleConfig",)

from django.apps import AppConfig


class RateMyModuleConfig(AppConfig):
    """Config class to hold application's definition & configuration settings."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ratemymodule"
    verbose_name = "RateMyModule"
