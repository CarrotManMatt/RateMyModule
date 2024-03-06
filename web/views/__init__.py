"""Web HTML views for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = ("HomeView", "UserSettingsView")

from typing import TYPE_CHECKING, override
from urllib.parse import unquote_plus

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from ratemymodule.models import Module, Post, University
from web.views import graph_utils

if TYPE_CHECKING:
    from django.db.models import QuerySet


class HomeView(TemplateView):
    """Main Dashboard view, for users to look at the most recent posts about uni modules."""

    template_name = "ratemymodule/home.html"

    @override
    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        # noinspection PyArgumentList
        module_code: str | None = self.request.GET.get("module")
        if module_code is None:
            university: University = (
                self.request.user.university
                if self.request.user.is_authenticated and self.request.user.university
                else University.objects.get(name="The University of Birmingham")
            )
            if university.module_set.exists():
                return redirect(
                    f"{reverse("ratemymodule:home")}?"
                    f"{urlencode({"module": university.module_set.all()[0].code})}"
                )

        return super().get(request, *args, **kwargs)

    # noinspection PyMethodMayBeStatic
    def _get_graphs_context_data(self, context_data: dict[str, object]) -> dict[str, object]:
        if not Post.objects.exists():
            return {
                "overall_rating_bar_graph": "",
                "difficulty_bar_graph": "",
                "teaching_graph": "",
                "assessment_graph": "",
                **context_data
            }

        return {
            "overall_rating_bar_graph": mark_safe(graph_utils.overall_rating_bar_graph()),  # noqa: S308
            "difficulty_bar_graph": mark_safe(graph_utils.difficulty_rating_bar_graph()),  # noqa: S308
            "teaching_graph": mark_safe(graph_utils.teaching_quality_bar_graph()),  # noqa: S308
            "assessment_graph": mark_safe(graph_utils.assessment_quality_bar_graph()),  # noqa: S308
            **context_data
        }

    def _get_post_list_context_data(self, context_data: dict[str, object]) -> dict[str, object]:  # noqa: E501
        try:
            # noinspection PyTypeChecker
            module: Module = Module.objects.get(code=unquote_plus(self.request.GET["module"]))
        except Module.DoesNotExist:
            return {"error": _("Error: Module Not Found"), **context_data}

        post_set: QuerySet[Post] = module.post_set.all().order_by("date_time_created")

        # noinspection PyArgumentList
        raw_search_string: str | None = self.request.GET.get("q")
        if raw_search_string:
            post_set = post_set.filter(content__icontains=unquote_plus(raw_search_string))

        # noinspection PyArgumentList
        raw_rating: str | None = self.request.GET.get("rating")
        if raw_rating:
            try:
                rating: Post.Ratings = Post.Ratings(int(unquote_plus(raw_rating)))
            except ValueError:
                return {"error": _("Error: Incorrect rating value"), **context_data}

            post_set = post_set.filter(overall_rating=rating)

        # noinspection PyArgumentList
        raw_year: str | None = self.request.GET.get("year")
        if raw_year:
            try:
                year: int = int(unquote_plus(raw_year))
            except ValueError:
                return {"error": _("Error: Incorrect rating value"), **context_data}

            post_set = post_set.filter(academic_year_start=year)

        return {"post_list": post_set, **context_data}

    @override
    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context_data: dict[str, object] = super().get_context_data(**kwargs)

        context_data["course_list"] = (
            (
                self.request.user.university
                if self.request.user.is_authenticated and self.request.user.university
                else University.objects.get(name="The University of Birmingham")
            ).course_set.prefetch_related("module_set").all()
        )

        context_data = self._get_graphs_context_data(context_data)
        context_data = self._get_post_list_context_data(context_data)

        return context_data  # noqa: RET504


class UserSettingsView(TemplateView):
    """Account management view, for users to edit their account settings."""

    template_name = "ratemymodule/user-settings.html"
