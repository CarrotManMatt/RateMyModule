"""Root URL configuration for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns",)

import django
from django.contrib import admin
from django.urls import URLPattern, URLResolver
from django.views.generic import RedirectView

from core.views import AdminDocsRedirectView

urlpatterns: list[URLResolver | URLPattern] = [
    django.urls.path(
        r"admin/doc/",
        django.urls.include("django.contrib.admindocs.urls")
    ),
    django.urls.path(r"admin/docs/", AdminDocsRedirectView.as_view()),
    django.urls.path(
        r"admin/docs/<path:subpath>",
        AdminDocsRedirectView.as_view()
    ),
    django.urls.path(r"admin/", admin.site.urls),
    django.urls.path(r"accounts/", django.urls.include("allauth.urls")),  # NOTE: This URL group should be removed once all login methods are implemented within the `ratemymodule` app
    django.urls.path(r"api/htmx/", django.urls.include("api_htmx.urls")),
    django.urls.path("", django.urls.include("web.urls")),
    django.urls.path(
        "",
        RedirectView.as_view(pattern_name="ratemymodule:home"),
        name="default"
    )
]
