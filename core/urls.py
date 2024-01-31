"""Root URL configuration for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns",)

from collections.abc import MutableSequence

import django
from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver
from django.views.generic import RedirectView

from core.views import AdminDocsRedirectView

urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    django.urls.path(
        r"admin/doc/",
        django.urls.include("django.contrib.admindocs.urls")
    ),
    django.urls.path(r"admin/docs/", AdminDocsRedirectView.as_view()),
    django.urls.path(
        r"admin/docs/<path:subpath>",
        AdminDocsRedirectView.as_view()
    ),
    django.urls.path(r"admin/", admin.site.urls, name="admin"),
    django.urls.path(r"api/htmx/", django.urls.include("api_htmx.urls")),
    django.urls.path(r"", django.urls.include("web.urls")),
    django.urls.path(
        r"",
        RedirectView.as_view(pattern_name="ratemymodule:home"),
        name="default"
    )
]

if settings.DEBUG:
    urlpatterns.append(
        django.urls.path(
            r"accounts/",
            django.urls.include("allauth.urls"),
            name="debug-accounts"
        )
    )
