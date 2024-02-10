"""URL configuration for `web` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns",)

from collections.abc import MutableSequence

import django
from django.urls import URLPattern, URLResolver

from web.views import HomeView

urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    django.urls.path(r"", HomeView.as_view(), name="home"),
]
