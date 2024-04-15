"""Root URL configuration for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns",)

from collections.abc import MutableSequence

import django
from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import URLPattern, URLResolver
from django.views.generic import RedirectView

from core.views import AdminDocsRedirectView

urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    django.urls.path(
        r".well-known/microsoft-identity-association.json",
        lambda _: JsonResponse(
            {
                "associatedApplications": [
                    {
                        "applicationId": (
                            settings.SOCIALACCOUNT_PROVIDERS["microsoft"]["APP"]["client_id"]  # type: ignore[index]
                        ),
                    },
                ],
            },
        ),
        name="microsoft-oauth-domain-verification",
    ),
    django.urls.path(
        r"admin/doc/",
        django.urls.include("django.contrib.admindocs.urls"),
    ),
    django.urls.path(r"admin/docs/", AdminDocsRedirectView.as_view()),
    django.urls.path(
        r"admin/docs/<path:subpath>",
        AdminDocsRedirectView.as_view(),
    ),
    django.urls.path(r"admin/", admin.site.urls),
    django.urls.path(r"api/htmx/", django.urls.include("api_htmx.urls")),
    django.urls.path(r"api/rest/", django.urls.include("api_rest.urls")),
    django.urls.path(r"", django.urls.include("web.urls")),
    django.urls.path(
        r"",
        RedirectView.as_view(pattern_name="ratemymodule:home"),
        name="default",
    ),
    django.urls.path(
        r"accounts/",
        django.urls.include("allauth.urls"),  # HACK: Temporarily include allauth URLs until they have all been implemented manually
        name="debug-accounts",
    )  # noqa: COM812
]
