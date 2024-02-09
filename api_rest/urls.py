"""URL configuration for `api_rest` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns",)

from collections.abc import MutableSequence

from django.urls import URLPattern, URLResolver

urlpatterns: MutableSequence[URLResolver | URLPattern] = []
