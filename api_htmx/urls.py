"""URL configuration for `api_htmx` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("urlpatterns", "app_name")

from collections.abc import MutableSequence
from typing import Final

import django.urls
from django.urls import URLPattern, URLResolver

from api_htmx.views import DislikePostView, LikePostView, UnlikePostView

app_name: Final[str] = "api_htmx"

urlpatterns: MutableSequence[URLResolver | URLPattern] = [
    django.urls.path(
        r"post/like/<int:pk>/",
        LikePostView.as_view(),
        name="like_post",
    ),
    django.urls.path(
        r"post/dislike/<int:pk>/",
        DislikePostView.as_view(),
        name="dislike_post",
    ),
    django.urls.path(
        r"post/unlike/<int:pk>/",
        UnlikePostView.as_view(),
        name="unlike_post",
    ),
]
