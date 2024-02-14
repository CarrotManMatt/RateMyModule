"""URL configuration for `api_rest` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns",)

from collections.abc import MutableSequence
from typing import Final

from django.urls import URLPattern, URLResolver

app_name: Final[str] = "api_rest"

urlpatterns: MutableSequence[URLResolver | URLPattern] = []
