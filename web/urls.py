"""URL configuration for `web` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns",)

from collections.abc import MutableSequence

import django
from django.urls import URLPattern, URLResolver
from django.views import defaults as default_views

urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    django.urls.path(r"", default_views.server_error, name="home"),
]
