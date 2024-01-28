"""URL configuration for `web` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns",)

from django.urls import URLPattern, URLResolver

urlpatterns: list[URLResolver | URLPattern] = []
