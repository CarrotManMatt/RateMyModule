"""URL configuration for `web` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns",)

from collections.abc import MutableSequence
from typing import Final

import django
from django.urls import URLPattern, URLResolver
from django.views.generic import RedirectView

from web.views import HomeView, UserSettingsView, SubmitPostView, LogoutView

app_name: Final[str] = "ratemymodule"

view_urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    django.urls.path(r"", HomeView.as_view(), name="home"),
    django.urls.path(
        r"submit-review/",
        SubmitPostView.as_view(),
        name="submit-review"
    ),
    django.urls.path(
        r"settings/",
        UserSettingsView.as_view(),
        name="user-settings"
    ),
    django.urls.path(r"logout/", LogoutView.as_view(), name="logout")
]

favicon_urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    django.urls.path(
        r"favicon.ico",
        RedirectView.as_view(url=r"/static/ratemymodule/favicon/favicon.ico",
                             permanent=True),
        name="favicon_redirect"
    ),
    django.urls.path(
        r"android-chrome-192x192.png",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/android-chrome-192x192.png",
            permanent=True
        ),
        name="chrome_favicon_192_redirect"
    ),
    django.urls.path(
        r"android-chrome-512x512.png",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/android-chrome-512x512.png",
            permanent=True
        ),
        name="chrome_favicon_512_redirect"
    ),
    django.urls.path(
        r"apple-touch-icon.png",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/apple-touch-icon.png",
            permanent=True
        ),
        name="apple_favicon_redirect"
    ),
    django.urls.path(
        r"browserconfig.xml",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/browserconfig.xml",
            permanent=True
        ),
        name="browser_config_redirect"
    ),
    django.urls.path(
        r"favicon.svg",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/favicon.svg",
            permanent=True
        ),
        name="svg_favicon_redirect"
    ),
    django.urls.path(
        r"favicon-16x16.png",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/favicon-16x16.png",
            permanent=True
        ),
        name="favicon_16_redirect"
    ),
    django.urls.path(
        r"favicon-32x32.png",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/favicon-32x32.png",
            permanent=True
        ),
        name="favicon_32_redirect"
    ),
    django.urls.path(
        r"mstile-70x70.png",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/mstile-70x70.png",
            permanent=True
        ),
        name="microsoft_favicon_70_redirect"
    ),
    django.urls.path(
        r"mstile-144x144.png",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/mstile-144x144.png",
            permanent=True
        ),
        name="microsoft_favicon_144_redirect"
    ),
    django.urls.path(
        r"mstile-150x150.png",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/mstile-150x150.png",
            permanent=True
        ),
        name="microsoft_favicon_150_redirect"
    ),
    django.urls.path(
        r"mstile-310x150.png",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/mstile-310x150.png",
            permanent=True
        ),
        name="microsoft_favicon_310x150_redirect"
    ),
    django.urls.path(
        r"mstile-310x310.png",
        RedirectView.as_view(
            url=r"/static/ratemymodule/favicon/mstile-310x310.png",
            permanent=True
        ),
        name="microsoft_favicon_310_redirect"
    )
]

urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    *view_urlpatterns,
    *favicon_urlpatterns
]
