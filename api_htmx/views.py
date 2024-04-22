"""HTMX API views for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = ("LikePostView", "DislikePostView", "UnlikePostView")

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.views.generic import DetailView

from ratemymodule.models import Post


class LikePostView(LoginRequiredMixin, DetailView[Post]):
    http_method_names = ("post",)
    template_name = "ratemymodule/fragments/like-dislike-buttons.html"
    context_object_name = "post"

    @override
    def get_queryset(self) -> QuerySet[Post]:
        return Post.filter_by_viewable(request=self.request).all()

    # noinspection PyOverrides
    @override
    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        self.object: Post = self.get_object()

        if not self.request.user.is_authenticated:
            raise RuntimeError

        self.object.user_like(self.request.user)

        self.object.refresh_from_db()

        return self.render_to_response(self.get_context_data(object=self.object))


class DislikePostView(LoginRequiredMixin, DetailView[Post]):
    http_method_names = ("post",)
    template_name = "ratemymodule/fragments/like-dislike-buttons.html"
    context_object_name = "post"

    @override
    def get_queryset(self) -> QuerySet[Post]:
        return Post.filter_by_viewable(request=self.request).all()

    # noinspection PyOverrides
    @override
    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        self.object: Post = self.get_object()

        if not self.request.user.is_authenticated:
            raise RuntimeError

        self.object.user_dislike(self.request.user)

        self.object.refresh_from_db()

        return self.render_to_response(self.get_context_data(object=self.object))


class UnlikePostView(LoginRequiredMixin, DetailView[Post]):
    http_method_names = ("post",)
    template_name = "ratemymodule/fragments/like-dislike-buttons.html"
    context_object_name = "post"

    @override
    def get_queryset(self) -> QuerySet[Post]:
        return Post.filter_by_viewable(request=self.request).all()

    # noinspection PyOverrides
    @override
    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        self.object: Post = self.get_object()

        if not self.request.user.is_authenticated:
            raise RuntimeError

        self.object.user_unlike(self.request.user)

        self.object.refresh_from_db()

        return self.render_to_response(self.get_context_data(object=self.object))
