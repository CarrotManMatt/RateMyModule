"""Web HTML views for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "HomeView",
    "SubmitPostView",
    "UserSettingsView",
    "LogoutView",
    "LoginView",
    "SignupView",
)

import re
from typing import TYPE_CHECKING, override
from urllib.parse import unquote_plus

import django
from allauth.account.views import LogoutView as AllAuthLogoutView
from allauth.account.views import LoginView as AllAuthLoginView
from allauth.account.views import SignupView as AllAuthSignupView
from allauth.account.forms import LoginForm
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView

from ratemymodule.models import Module, Post, University, User
from web.forms import PostForm, SignupForm
from web.views import graph_utils

if TYPE_CHECKING:
    from django.db.models import QuerySet


class LogoutView(AllAuthLogoutView):  # type: ignore[misc,no-any-unimported]
    http_method_name = ["post"]


class LoginView(AllAuthLoginView):  # type: ignore[misc,no-any-unimported]
    http_method_names = ["post"]
    redirect_authenticated_user = True
    prefix = "login"

    def form_invalid(self, form: LoginForm) -> HttpResponseRedirect:  # type: ignore[no-any-unimported]
        if "login_form" in self.request.session:
            self.request.session.pop("login_form")

        self.request.session["login_form"] = {
            "data": form.data,
            "errors": form.errors
        }

        return django.shortcuts.redirect(settings.LOGIN_URL)


class SignupView(AllAuthSignupView):  # type: ignore[misc,no-any-unimported]
    http_method_names = ["post"]
    redirect_authenticated_user = True
    prefix = "signup"

    def form_invalid(self, form: SignupForm) -> HttpResponseRedirect:  # type: ignore[no-any-unimported]
        if "signup_form" in self.request.session:
            self.request.session.pop("signup_form")

        self.request.session["signup_form"] = {
            "data": form.data,
            "errors": form.errors
        }

        return django.shortcuts.redirect(settings.SIGNUP_URL)


class HomeView(TemplateView):
    """Main Dashboard view, for users to look at the most recent posts about uni modules."""

    template_name = "ratemymodule/home.html"
    http_method_names = ["get"]

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

        try:
            # noinspection PyTypeChecker
            module: Module = Module.objects.get(code=unquote_plus(self.request.GET["module"]))
        except Module.DoesNotExist:
            return {**context_data, "error": _("Error: Module Not Found")}

        # noinspection SpellCheckingInspection
        return {
            **context_data,
            "overall_rating_bar_graph": mark_safe(  # noqa: S308
                re.sub(
                    "#aaaaaa",
                    "var(--text-color)",
                    re.sub(
                        "#ffffff",
                        "var(--button-color)",
                        graph_utils.overall_rating_bar_graph(
                            module,
                            "ffffff",
                            "aaaaaa",
                        ),
                    ),
                )  # noqa: COM812
            ),
            "difficulty_bar_graph": mark_safe(  # noqa: S308
                re.sub(
                    "#aaaaaa",
                    "var(--text-color)",
                    re.sub(
                        "#ffffff",
                        "var(--button-color)",
                        graph_utils.difficulty_rating_bar_graph(
                            module,
                            "ffffff",
                            "aaaaaa",
                        ),
                    ),
                )  # noqa: COM812
            ),
            "teaching_graph": mark_safe(  # noqa: S308
                re.sub(
                    "#aaaaaa",
                    "var(--text-color)",
                    re.sub(
                        "#ffffff",
                        "var(--button-color)",
                        graph_utils.teaching_quality_bar_graph(
                            module,
                            "ffffff",
                            "aaaaaa",
                        ),
                    ),
                )  # noqa: COM812
            ),
            "assessment_graph": mark_safe(  # noqa: S308
                re.sub(
                    "#aaaaaa",
                    "var(--text-color)",
                    re.sub(
                        "#ffffff",
                        "var(--button-color)",
                        graph_utils.assessment_quality_bar_graph(
                            module,
                            "ffffff",
                            "aaaaaa",
                        ),
                    ),
                )  # noqa: COM812
            ),
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

    def _get_login_forms_context_data(self, context_data: dict[str, object]) -> dict[str, object]:  # noqa: E501
        if "login_form" not in context_data:
            if "login_form" not in self.request.session:
                context_data["login_form"] = LoginForm(prefix="login")

            else:
                login_form = LoginForm(
                    data=self.request.session["login_form"]["data"],
                    request=self.request,
                    prefix="login"
                )
                login_form.is_valid()

                context_data["login_form"] = login_form

                self.request.session.pop("login_form")

        if "signup_form" not in context_data:
            if "signup_form" not in self.request.session:
                context_data["signup_form"] = SignupForm(prefix="signup")

            else:
                signup_form = SignupForm(
                    data=self.request.session["signup_form"]["data"],
                    prefix="signup"
                )
                signup_form.is_valid()

                context_data["signup_form"] = signup_form

                self.request.session.pop("signup_form")

        return context_data

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
        context_data = self._get_login_forms_context_data(context_data)

        return context_data  # noqa: RET504


class SubmitPostView(LoginRequiredMixin, CreateView[Post, PostForm]):
    """SubmitPostView for handling module review submissions."""

    template_name = "ratemymodule/submit-review.html"
    form_class = PostForm
    success_url = "/"  # TODO: change to reverse url lookup
    model = Post
    http_method_names = ["get", "post"]

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


class UserSettingsView(LoginRequiredMixin, TemplateView):
    """Account management view, for users to edit their account settings."""

    template_name = "ratemymodule/user-settings.html"
    http_method_names = ["get"]
