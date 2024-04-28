"""URL configuration for `web` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns", "app_name")

from collections.abc import MutableSequence
from typing import Final

import django.urls
from django.templatetags.static import static
from django.urls import URLPattern, URLResolver
from django.views.generic import RedirectView

from web.views import (
    ChangeCoursesView,
    ChangeEmailView,
    ChangePasswordView,
    DeleteAccountView,
    HomeView,
    LoginView,
    LogoutView,
    OtherTagAutocompleteView,
    SignupView,
    SubmitPostView,
    SubmitReportView,
    ToolTagAutocompleteView,
    TopicTagAutocompleteView,
)

app_name: Final[str] = "ratemymodule"

view_urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    django.urls.path(r"", HomeView.as_view(), name="home"),
    django.urls.path(
        r"submit-review/",
        SubmitPostView.as_view(),
        name="submit_review",
    ),
    django.urls.path(
        r"settings/change/email",
        ChangeEmailView.as_view(),
        name="change_email",
    ),
    django.urls.path(
        r"settings/change/password",
        ChangePasswordView.as_view(),
        name="change_password",
    ),
    django.urls.path(
        r"settings/change/courses",
        ChangeCoursesView.as_view(),
        name="change_courses",
    ),
    django.urls.path(
        r"settings/delete-account",
        DeleteAccountView.as_view(),
        name="delete_account",
    ),
    django.urls.path(r"logout/", LogoutView.as_view(), name="logout"),
    django.urls.path(r"login/", LoginView.as_view(), name="login"),
    django.urls.path(r"signup/", SignupView.as_view(), name="signup"),
    django.urls.path(
        r"submit-report/",
        SubmitReportView.as_view(),
        name="submit_report",
    ),
    django.urls.path(
        "autocomplete/tool_tags",
        ToolTagAutocompleteView.as_view(),
        name="autocomplete_tool_tags",
    ),
    django.urls.path(
        "autocomplete/topic_tags",
        TopicTagAutocompleteView.as_view(),
        name="autocomplete_topic_tags",
    ),
    django.urls.path(
        "autocomplete/other_tags",
        OtherTagAutocompleteView.as_view(),
        name="autocomplete_other_tags",
    ),
]

favicon_urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    django.urls.path(
        r"favicon.ico",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/favicon.ico"),
            permanent=False,
        ),
        name="favicon_redirect",
    ),
    django.urls.path(
        r"android-chrome-192x192.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/android-chrome-192x192.png"),
            permanent=False,
        ),
        name="chrome_favicon_192_redirect",
    ),
    django.urls.path(
        r"android-chrome-384x384.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/android-chrome-384x384.png"),
            permanent=False,
        ),
        name="chrome_favicon_384_redirect",
    ),
    django.urls.path(
        r"android-chrome-512x512.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/android-chrome-512x512.png"),
            permanent=False,
        ),
        name="chrome_favicon_512_redirect",
    ),
    django.urls.path(
        r"apple-touch-icon.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/apple-touch-icon.png"),
            permanent=False,
        ),
        name="apple_favicon_redirect",
    ),
    django.urls.path(
        r"browserconfig.xml",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/browserconfig.xml"),
            permanent=False,
        ),
        name="browser_config_redirect",
    ),
    django.urls.path(
        r"site.webmanifest",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/site.webmanifest"),
            permanent=False,
        ),
        name="site_webmanifest_redirect",
    ),
    django.urls.path(
        r"favicon.svg",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/favicon.svg"),
            permanent=False,
        ),
        name="svg_favicon_redirect",
    ),
    django.urls.path(
        r"favicon-16x16.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/favicon-16x16.png"),
            permanent=False,
        ),
        name="favicon_16_redirect",
    ),
    django.urls.path(
        r"favicon-32x32.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/favicon-32x32.png"),
            permanent=False,
        ),
        name="favicon_32_redirect",
    ),
    django.urls.path(
        r"mstile-70x70.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/mstile-70x70.png"),
            permanent=False,
        ),
        name="microsoft_favicon_70_redirect",
    ),
    django.urls.path(
        r"mstile-144x144.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/mstile-144x144.png"),
            permanent=False,
        ),
        name="microsoft_favicon_144_redirect",
    ),
    django.urls.path(
        r"mstile-150x150.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/mstile-150x150.png"),
            permanent=False,
        ),
        name="microsoft_favicon_150_redirect",
    ),
    django.urls.path(
        r"mstile-310x150.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/mstile-310x150.png"),
            permanent=False,
        ),
        name="microsoft_favicon_310x150_redirect",
    ),
    django.urls.path(
        r"mstile-310x310.png",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/mstile-310x310.png"),
            permanent=False,
        ),
        name="microsoft_favicon_310_redirect",
    ),
    django.urls.path(
        r"safari-pinned-tab.svg",
        RedirectView.as_view(
            url=static("ratemymodule/favicon/safari-pinned-tab.svg"),
            permanent=False,
        ),
        name="svg_safari_pinned_tab",
    ),
]

urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    *view_urlpatterns,
    *favicon_urlpatterns,
]
