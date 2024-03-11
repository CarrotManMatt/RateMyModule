"""Web HTML views for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "HomeView",
    "SubmitPostView",
    "UserSettingsView",
    "LogoutView",
)

from typing import TYPE_CHECKING, override
from urllib.parse import unquote_plus

from allauth.account.views import LogoutView as AllAuthLogoutView
from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, QueryDict
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView

from ratemymodule.models import Module, Post, University, User
from web.forms import PostForm
from web.views import graph_utils

if TYPE_CHECKING:
    from django.db.models import QuerySet


class LogoutView(AllAuthLogoutView):  # type: ignore[misc,no-any-unimported]
    @override
    def get(self, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        raise Http404


class HomeView(TemplateView):
    """Main Dashboard view, for users to look at the most recent posts about uni modules."""

    template_name = "ratemymodule/home.html"

    @override
    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        # noinspection PyArgumentList
        signup_action: str | None = self.request.GET.get("action")
        if signup_action == "signup":
            # noinspection PyArgumentList
            signup_get_params: QueryDict = self.request.GET.copy()
            signup_get_params["action"] = "login"
            return redirect(f"{self.request.path}?{signup_get_params.urlencode()}")

        # noinspection PyArgumentList
        module_code: str | None = self.request.GET.get("module")
        if module_code is None:
            university: University = (
                self.request.user.university
                if self.request.user.is_authenticated and self.request.user.university
                else University.objects.get(name="The University of Birmingham")
            )
            if university.module_set.exists():
                get_params: QueryDict = QueryDict(mutable=True)
                get_params["module"] = university.module_set.all()[0].code

                # noinspection PyArgumentList
                action: str | None = self.request.GET.get("action")
                if action is not None:
                    get_params["action"] = action

                return redirect(f"{self.request.path}?{get_params.urlencode()}")

        return super().get(request, *args, **kwargs)

    # noinspection PyMethodMayBeStatic
    def _get_graphs_context_data(self, context_data: dict[str, object]) -> dict[str, object]:
        if not Post.objects.exists():
            return {
                **context_data,
                "overall_rating_bar_graph": "",
                "difficulty_bar_graph": "",
                "teaching_graph": "",
                "assessment_graph": "",
            }

        return {
            **context_data,
            "overall_rating_bar_graph": mark_safe(graph_utils.overall_rating_bar_graph()),  # noqa: S308
            "difficulty_bar_graph": mark_safe(graph_utils.difficulty_rating_bar_graph()),  # noqa: S308
            "teaching_graph": mark_safe(graph_utils.teaching_quality_bar_graph()),  # noqa: S308
            "assessment_graph": mark_safe(graph_utils.assessment_quality_bar_graph()),  # noqa: S308
        }

    def _get_post_list_context_data(self, context_data: dict[str, object]) -> dict[str, object]:  # noqa: E501
        try:
            # noinspection PyTypeChecker
            module: Module = Module.objects.get(code=unquote_plus(self.request.GET["module"]))
        except Module.DoesNotExist:
            return {**context_data, "error": _("Error: Module Not Found")}

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
                return {**context_data, "error": _("Error: Incorrect rating value")}

            post_set = post_set.filter(overall_rating=rating)

        # noinspection PyArgumentList
        raw_year: str | None = self.request.GET.get("year")
        if raw_year:
            try:
                year: int = int(unquote_plus(raw_year))
            except ValueError:
                return {**context_data, "error": _("Error: Incorrect rating value")}

            post_set = post_set.filter(academic_year_start=year)

        return {**context_data, "post_list": post_set}

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

        context_data["LOGIN_URL"] = settings.LOGIN_URL

        context_data = self._get_graphs_context_data(context_data)
        context_data = self._get_post_list_context_data(context_data)

        return context_data  # noqa: RET504


class SubmitPostView(CreateView[Post, PostForm]):
    """SubmitPostView for handling module review submissions."""

    template_name = "ratemymodule/submit-review.html"
    form_class = PostForm
    success_url = "/"
    model = Post

    # noinspection PyOverrides
    @override
    def form_valid(self, form: PostForm) -> HttpResponse:
        obj = form.save(commit=False)
        if not User.objects.exists():
            raise User.DoesNotExist
        obj.user = User.objects.all()[0]
        return super().form_valid(form)

    # noinspection PyOverrides
    @override
    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context["module_choices"] = Module.objects.all()
        context["academic_year_choices"] = (
            self.form_class.ACADEMIC_YEAR_CHOICES
        )
        return context


class UserSettingsView(TemplateView):
    """Account management view, for users to edit their account settings."""

    template_name = "ratemymodule/user-settings.html"
