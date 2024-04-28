"""Web HTML views for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "HomeView",
    "SubmitPostView",
    "ChangeEmailView",
    "ChangePasswordView",
    "ChangeCoursesView",
    "DeleteAccountView",
    "LogoutView",
    "LoginView",
    "SignupView",
    "ToolTagAutocompleteView",
    "TopicTagAutocompleteView",
    "OtherTagAutocompleteView",
    "SubmitReportView",
)

import contextlib
import re
from collections.abc import Container, MutableSet
from typing import TYPE_CHECKING, Final, override
from urllib.parse import unquote_plus

import django
import django.shortcuts
from allauth.account.forms import LoginForm
from allauth.account.views import EmailView as AllAuthEmailView
from allauth.account.views import LoginView as AllAuthLoginView
from allauth.account.views import LogoutView as AllAuthLogoutView
from allauth.account.views import PasswordChangeView as AllAuthPasswordChangeView
from allauth.account.views import SignupView as AllAuthSignupView
from django import forms, urls
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
    QueryDict,
)
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, FormView, TemplateView

from ratemymodule.models import (
    Course,
    Module,
    OtherTag,
    Post,
    ToolTag,
    TopicTag,
    University,
    User,
)
from web.forms import AnalyticsForm, ChangeCoursesForm, PostForm, ReportForm, SignupForm

from . import graph_generators, utils
from .utils import EnsureUserHasCoursesMixin, NextURLRemovedFromGETParams

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser
    from django.db.models import QuerySet


class LogoutView(AllAuthLogoutView):  # type: ignore[misc,no-any-unimported]
    """The view for logging out the user."""

    http_method_names = ("post",)


class LoginView(AllAuthLoginView):  # type: ignore[misc,no-any-unimported]
    """The view for processing login requests."""

    http_method_names = ("get", "post")
    redirect_authenticated_user = True
    prefix = "login"

    @override
    def get(self, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        return django.shortcuts.redirect(utils.get_login_url_from_request(self.request))

    @override
    def form_invalid(self, form: LoginForm) -> HttpResponseRedirect:  # type: ignore[misc,no-any-unimported]
        if "login_form" in self.request.session:
            self.request.session.pop("login_form")

        self.request.session["login_form"] = {
            "data": form.data,
            "errors": form.errors,
        }

        extra_get_params: QueryDict = QueryDict("", mutable=True)
        # noinspection PyTypeChecker
        next_url: str | None = self.request.POST.get("login-next", None)
        if next_url:
            extra_get_params["next"] = next_url
        extra_get_params.update(self.request.GET)

        return django.shortcuts.redirect(
            utils.get_login_url_with_extra_params(extra_get_params),
        )

    @override
    def get_success_url(self) -> str:  # type: ignore[misc]
        # noinspection PyTypeChecker
        next_url: str | None = self.request.POST.get("login-next", None)

        return next_url if next_url else super().get_success_url()  # type: ignore[no-any-return]


class SignupView(AllAuthSignupView):  # type: ignore[misc,no-any-unimported]
    """A view for signing up a new user."""

    http_method_names = ("get", "post")
    redirect_authenticated_user = True
    prefix = "signup"

    @override
    def get(self, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        return django.shortcuts.redirect(utils.get_signup_url_from_request(self.request))

    @override
    def form_invalid(self, form: SignupForm) -> HttpResponseRedirect:  # type: ignore[misc]
        if "signup_form" in self.request.session:
            self.request.session.pop("signup_form")

        self.request.session["signup_form"] = {
            "data": form.data,
            "errors": form.errors,
        }

        extra_get_params: QueryDict = QueryDict("", mutable=True)
        # noinspection PyTypeChecker
        next_url: str | None = self.request.POST.get("signup-next", None)
        if next_url:
            extra_get_params["next"] = next_url
        extra_get_params.update(self.request.GET)

        return django.shortcuts.redirect(
            utils.get_signup_url_with_extra_params(extra_get_params),
        )

    @override
    def get_success_url(self) -> str:  # type: ignore[misc]
        # noinspection PyTypeChecker
        next_url: str | None = self.request.POST.get("signup-next", None)

        return next_url if next_url else super().get_success_url()  # type: ignore[no-any-return]


class HomeView(EnsureUserHasCoursesMixin, TemplateView):
    """Main Dashboard view, for users to look at the most recent posts about uni modules."""

    template_name = "ratemymodule/home.html"
    http_method_names = ("get",)

    @classmethod
    def _remove_next_url_from_get_params(cls, get_params: QueryDict) -> NextURLRemovedFromGETParams:  # noqa: E501
        raw_next_url: list[str] | None = get_params.pop("next", None)  # type: ignore[assignment]
        return NextURLRemovedFromGETParams(
            next_url=raw_next_url[0] if raw_next_url and raw_next_url[0] else None,
            returned_get_params=get_params,
        )

    @override
    def get(self, *args: object, **kwargs: object) -> HttpResponse:
        # noinspection PyArgumentList
        returned_get_params: QueryDict = self.request.GET.copy()

        MODULE_CODE: Final[str | None] = returned_get_params.get("module", None)
        if MODULE_CODE:
            with contextlib.suppress(Module.DoesNotExist):
                self.request.session["selected_module_pk"] = Module.objects.get(
                    code=unquote_plus(MODULE_CODE),
                ).pk

            returned_get_params.pop("module", None)

        _next_url_removed_from_get_params: NextURLRemovedFromGETParams = self._remove_next_url_from_get_params(  # noqa: E501
            returned_get_params,
        )
        NEXT_URL: Final[str | None] = _next_url_removed_from_get_params.next_url
        returned_get_params = _next_url_removed_from_get_params.returned_get_params

        action: str | None = returned_get_params.get("action", None)

        if action is not None:
            new_action: str = action.strip().replace("-", "_").strip()

            if not new_action:
                returned_get_params.pop("action", None)
                return django.shortcuts.redirect(
                    to=utils.get_reload_with_get_params_url(
                        self.request,
                        returned_get_params,
                    ),
                )

            if new_action != action:
                returned_get_params["action"] = new_action
                return django.shortcuts.redirect(
                    to=utils.get_reload_with_get_params_url(
                        self.request,
                        returned_get_params,
                    ),
                )

            ALLOWED_ACTIONS: Final[Container[str]] = (
                "signup",
                "login",
                "select_university",
                "generate_graph",
                "like",
                "dislike",
            )
            if action not in ALLOWED_ACTIONS:
                BAD_REQUEST_MESSAGE: Final[str] = f"{action!r} is not a valid action."
                raise BadRequest(BAD_REQUEST_MESSAGE)

        if action in ("login", "signup") and self.request.user.is_authenticated:
            if NEXT_URL:
                return django.shortcuts.redirect(NEXT_URL)

            login_signup_next_action: list[str] | None = returned_get_params.pop(  # type: ignore[assignment]
                "next_action",
                None,
            )
            LOGIN_SIGNUP_NEXT_ACTION_EXISTS: Final[bool] = bool(
                login_signup_next_action
                and login_signup_next_action[0]
                and login_signup_next_action[0] != "login"
                and login_signup_next_action[0] != "signup"  # noqa: COM812
            )
            if LOGIN_SIGNUP_NEXT_ACTION_EXISTS:
                returned_get_params["action"] = login_signup_next_action[0]  # type: ignore[index]
            else:
                returned_get_params.pop("action", None)

            return django.shortcuts.redirect(
                to=utils.get_reload_with_get_params_url(self.request, returned_get_params),
            )

        if action == "signup":
            returned_get_params["action"] = "login"
            return django.shortcuts.redirect(
                to=utils.get_reload_with_get_params_url(self.request, returned_get_params),
            )

        if action == "select_university":
            if not self.request.user.is_authenticated:
                # noinspection PyTypeChecker
                raw_university_pk: str | None = self.request.GET.get(
                    "university",
                    None  # noqa: COM812
                )
                if not raw_university_pk:
                    return django.shortcuts.render(
                        self.request,
                        "ratemymodule/university-selector.html",
                        {"university_choices": University.objects.all()},
                    )

                try:
                    selected_university: University = University.objects.get(
                        pk=raw_university_pk,
                    )
                except University.DoesNotExist:
                    returned_get_params.pop("university", None)
                    return django.shortcuts.redirect(
                        to=utils.get_reload_with_get_params_url(
                            self.request,
                            returned_get_params,
                        ),
                    )

                self.request.session["selected_university_pk"] = selected_university.pk

            if NEXT_URL:
                return django.shortcuts.redirect(to=NEXT_URL)

            select_university_next_action: list[str] | None = returned_get_params.pop(  # type: ignore[assignment]
                "next_action",
                None,
            )
            if select_university_next_action and select_university_next_action[0]:
                returned_get_params["action"] = select_university_next_action[0]
            else:
                returned_get_params.pop("action", None)

            returned_get_params.pop("university", None)

            return django.shortcuts.redirect(
                to=utils.get_reload_with_get_params_url(self.request, returned_get_params),
            )

        NO_SELECTED_UNIVERSITY: bool = (
            not self.request.user.is_authenticated
            and not self.request.session.get("selected_university_pk", None)
        )
        if NO_SELECTED_UNIVERSITY:
            if NEXT_URL:
                returned_get_params["next"] = NEXT_URL
            elif action:
                returned_get_params["next_action"] = action

            returned_get_params["action"] = "select_university"
            returned_get_params.pop("university", None)

            return django.shortcuts.redirect(
                to=utils.get_reload_with_get_params_url(self.request, returned_get_params),
            )

        if NEXT_URL and self.request.user.is_authenticated:
            return django.shortcuts.redirect(to=NEXT_URL)

        if MODULE_CODE:
            return django.shortcuts.redirect(
                to=utils.get_reload_with_get_params_url(self.request, returned_get_params),
            )

        return super().get(*args, **kwargs)  # type: ignore[arg-type]

    # noinspection PyMethodMayBeStatic
    def _get_graphs_context_data(self, selected_module: Module) -> dict[str, object]:
        if not Post.objects.exists():
            return {
                "overall_rating_bar_graph": "",
                "difficulty_bar_graph": "",
                "teaching_graph": "",
                "assessment_graph": "",
            }

        # noinspection SpellCheckingInspection
        return {
            "overall_rating_bar_graph": mark_safe(  # noqa: S308
                re.sub(
                    "#aaaaaa",
                    "var(--text-color)",
                    re.sub(
                        "#ffffff",
                        "var(--button-color)",
                        graph_generators.overall_rating_bar_graph(
                            selected_module,
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
                        graph_generators.difficulty_rating_bar_graph(
                            selected_module,
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
                        graph_generators.teaching_quality_bar_graph(
                            selected_module,
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
                        graph_generators.assessment_quality_bar_graph(
                            selected_module,
                            "ffffff",
                            "aaaaaa",
                        ),
                    ),
                )  # noqa: COM812
            ),
        }

    def _get_post_list_context_data(self, selected_module: Module) -> dict[str, object]:
        post_set: QuerySet[Post] = Post.filter_by_viewable(selected_module, self.request).all()

        # noinspection PyTypeChecker
        raw_search_string: str | None = self.request.GET.get("q", None)
        if raw_search_string:
            post_set = post_set.filter(content__icontains=unquote_plus(raw_search_string))

        # noinspection PyTypeChecker
        raw_rating: str | None = self.request.GET.get("rating", None)
        if raw_rating:
            try:
                rating: Post.Ratings = Post.Ratings(int(unquote_plus(raw_rating)))
            except ValueError:
                return {"error": _("Error: Incorrect rating value")}

            post_set = post_set.filter(overall_rating=rating)

        # noinspection PyTypeChecker
        raw_year: str | None = self.request.GET.get("year", None)
        if raw_year:
            try:
                year: int = int(unquote_plus(raw_year))
            except ValueError:
                return {"error": _("Error: Incorrect rating value")}

            post_set = post_set.filter(academic_year_start=year)

        # noinspection PyTypeChecker
        raw_tags: list[str] | None = self.request.GET.getlist("tags", None)
        if raw_tags:
            post_set = post_set & Post.filter_by_tags(
                tag_names=(tag.strip() for raw_tag in raw_tags for tag in raw_tag.split(",")),
            ).all()

        post_set = post_set.distinct()

        return {
            "post_list": post_set.order_by("-date_time_created"),
            "can_filter_by_tags": (
                ToolTag.objects.exists()
                or TopicTag.objects.exists()
                or OtherTag.objects.exists()
            ),
        }

    def _get_advanced_analytics_form_context_data(self, selected_module: Module, *, analytics_form_already_in_context_data: bool) -> dict[str, object]:  # noqa: E501
        if analytics_form_already_in_context_data:
            return {}

        # noinspection PyTypeChecker
        action: str | None = self.request.GET.get("action", None)

        if action != "generate_graph":
            return {"analytics_form": AnalyticsForm()}

        # first extract all data

        # noinspection PyTypeChecker
        difficulty_rating: str | None = self.request.GET.get(
            "aa_difficulty_rating", None,
        )
        # noinspection PyTypeChecker
        teaching_rating: str | None = self.request.GET.get(
            "aa_teaching_quality", None,
        )
        # noinspection PyTypeChecker
        assessment_quality: str | None = self.request.GET.get(
            "aa_assessment_quality", None,
        )
        # noinspection PyTypeChecker
        overall_rating: str | None = self.request.GET.get(
            "aa_overall_rating", None,
        )

        # noinspection PyTypeChecker
        start_year: int = int(self.request.GET["aa_start_year"])  # HACK: Cast to int, error checking is not performed
        # noinspection PyTypeChecker
        end_year: int = int(self.request.GET["aa_end_year"])  # HACK: Cast to int, error checking is not performed
        return {
            # repopulate form
            "analytics_form": AnalyticsForm(
                initial={
                    "aa_difficulty_rating": difficulty_rating,
                    "aa_teaching_quality": teaching_rating,
                    "aa_assessment_quality": assessment_quality,
                    "aa_overall_rating": overall_rating,
                    "aa_start_year": start_year,
                    "aa_end_year": end_year,
                },
            ),
            # pass data to graph and make it
            # noinspection PyTypeChecker
            "advanced_analytics_graph": mark_safe(  # noqa: S308
                re.sub(
                    "#000002",  # NOTE: Defines colour of the border of the legend box
                    "var(--button-hover)",
                    re.sub(
                        "#000001",  # NOTE: Defines colour of the legend box
                        "var(--secondary-color)",
                        re.sub(
                            "#aaaaaa",
                            "var(--text-color)",
                            graph_generators.advanced_analytics_graph(
                                module=selected_module,
                                difficulty_rating=(difficulty_rating == "on"),
                                teaching_rating=(teaching_rating == "on"),
                                assessment_quality=(assessment_quality == "on"),
                                overall_rating=(overall_rating == "on"),
                                start_year=start_year,
                                end_year=end_year,
                            ),
                        ),
                    ),
                ),
            ),
        }

    def _get_login_forms_context_data(self, *, login_form_already_in_context_data: bool, signup_form_already_in_context_data: bool) -> dict[str, object]:  # noqa: E501
        if not login_form_already_in_context_data:
            if "login_form" not in self.request.session:
                return {"login_form": LoginForm(prefix="login")}

            login_form: LoginForm = LoginForm(  # type: ignore[no-any-unimported]
                data=self.request.session["login_form"]["data"],
                request=self.request,
                prefix="login",
            )
            login_form.is_valid()
            self.request.session.pop("login_form")

            return {"login_form": login_form}

        if not signup_form_already_in_context_data:
            if "signup_form" not in self.request.session:
                return {"signup_form": SignupForm(prefix="signup")}

            signup_form: SignupForm = SignupForm(
                data=self.request.session["signup_form"]["data"],
                request=self.request,
                prefix="signup",
            )
            signup_form.is_valid()
            self.request.session.pop("signup_form")

            return {"signup_form": signup_form}

        return {}

    def _get_university_selection_context_data(self, university: University) -> dict[str, object]:  # noqa: E501
        # noinspection PyArgumentList
        select_university_get_params: QueryDict = self.request.GET.copy()
        select_university_get_params["action"] = "select_university"

        return {
            "selected_university": university,
            "select_university_url": utils.get_reload_with_get_params_url(
                self.request,
                select_university_get_params,
            ),
        }

    def _get_university_from_context_data(self) -> University:
        if self.request.user.is_authenticated:
            if self.request.user.university:
                return self.request.user.university

            raise Course.DoesNotExist

        try:
            return University.objects.get(
                pk=self.request.session.get("selected_university_pk", None),
            )
        except University.DoesNotExist:
            raise RuntimeError from None

    @override
    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context_data: dict[str, object] = super().get_context_data(**kwargs)

        university: University = self._get_university_from_context_data()

        if "selected_module_pk" not in self.request.session:
            self.request.session["selected_module_pk"] = university.module_set.all()[0].pk

        try:
            # noinspection PyTypeChecker
            selected_module: Module = Module.objects.get(
                pk=self.request.session["selected_module_pk"],
            )
        except Module.DoesNotExist:
            return {**context_data, "error": _("Error: Module Not Found")}

        return {
            **context_data,
            "LOGIN_URL": utils.get_login_url_from_request(self.request),
            "course_list": university.course_set.prefetch_related("module_set").all(),
            **self._get_university_selection_context_data(university),
            **self._get_graphs_context_data(selected_module),
            **self._get_post_list_context_data(selected_module),
            **self._get_login_forms_context_data(
                login_form_already_in_context_data="login_form" in context_data,
                signup_form_already_in_context_data="signup_form" in context_data,
            ),
            **self._get_advanced_analytics_form_context_data(
                selected_module,
                analytics_form_already_in_context_data="analytics_form" in context_data,
            ),
        }


class SubmitPostView(EnsureUserHasCoursesMixin, LoginRequiredMixin, CreateView[Post, PostForm]):  # noqa: E501
    """SubmitPostView for handling module review submissions."""

    template_name = "ratemymodule/submit-review.html"
    form_class = PostForm
    success_url = urls.reverse_lazy("default")
    model = Post
    http_method_names = ("get", "post")

    # noinspection PyOverrides
    @override
    def get_form_kwargs(self) -> dict[str, object]:
        return super().get_form_kwargs()

    # noinspection PyOverrides
    @override
    def form_valid(self, form: PostForm) -> HttpResponse:
        # noinspection PyAttributeOutsideInit
        self.object = form.save(commit=False)
        if not self.request.user.is_authenticated:  # HACK: Ensure the user is real
            raise RuntimeError
        self.object.user = self.request.user
        self.object.save()

        tag_fields = {
            "tool_tags": self.object.tool_tag_set,
            "topic_tags": self.object.topic_tag_set,
            "other_tags": self.object.other_tag_set,
        }

        for field, related_manager in tag_fields.items():
            tag_ids = []
            tag_names = form.cleaned_data.get(field, [])

            for tag_name in tag_names:
                if tag_name:
                    if tag_name.startswith("custom-"):
                        tag, created = related_manager.model.objects.get_or_create(  # type: ignore[attr-defined]
                            name=tag_name[7:].strip(),
                        )
                        tag_ids.append(tag.id)
                    else:
                        try:
                            tag_ids.append(int(tag_name))
                        except ValueError:
                            continue

            related_manager.set(tag_ids)  # type: ignore[attr-defined]

        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    # noinspection PyOverrides
    @override
    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)

        # Fetch the current user's enrolled courses
        user_enrolled_courses = (
            self.request.user.enrolled_course_set.all()
            if self.request.user.is_authenticated
            else Course.objects.none()
        )

        # Fetch modules for the user's enrolled courses
        user_module_choices = Module.objects.filter(
            course_set__in=user_enrolled_courses,
        ).distinct()

        context["module_choices"] = user_module_choices
        context["academic_year_choices"] = (
            self.form_class.ACADEMIC_YEAR_CHOICES
        )
        return context


class TopicTagAutocompleteView(View):
    """A view for processing GET requests about topic tags."""

    http_method_names = ("get",)

    # noinspection PyOverrides
    @override
    def get(self, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        # noinspection PyTypeChecker
        term = self.request.GET.get("term", "")
        tags = TopicTag.objects.filter(
            name__icontains=term,
            is_verified=True,
        ).values("id", "name")
        return JsonResponse(list(tags), safe=False)


class ToolTagAutocompleteView(View):
    """A view for processing GET requests for Tool tags."""

    http_method_names = ("get",)

    # noinspection PyOverrides
    @override
    def get(self, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        # noinspection PyTypeChecker
        term = self.request.GET.get("term", "")
        tags = ToolTag.objects.filter(
            name__icontains=term,
            is_verified=True,
        ).values("id", "name")
        return JsonResponse(list(tags), safe=False)


class OtherTagAutocompleteView(View):
    """A view for processing GET requests for other tags."""

    http_method_names = ("get",)

    # noinspection PyOverrides
    @override
    def get(self, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        # noinspection PyTypeChecker
        term = self.request.GET.get("term", "")
        tags = OtherTag.objects.filter(
            name__icontains=term,
            is_verified=True,
        ).values("id", "name")
        return JsonResponse(list(tags), safe=False)


class ChangeEmailView(LoginRequiredMixin, AllAuthEmailView):  # type: ignore[misc,no-any-unimported]
    """The view for showing and processing a user's change of email address."""

    template_name = "ratemymodule/change-email.html"
    http_method_names = ("get", "post")


class ChangePasswordView(LoginRequiredMixin, AllAuthPasswordChangeView):  # type: ignore[misc,no-any-unimported]
    """The view for showing and processing a user's change of password."""

    template_name = "ratemymodule/change-password.html"
    http_method_names = ("get", "post")


class ChangeCoursesView(LoginRequiredMixin, FormView[ChangeCoursesForm]):
    """The view for showing and processing a user's change of courses."""

    template_name = "ratemymodule/change-courses.html"
    http_method_names = ("get", "post")
    form_class = ChangeCoursesForm

    @override
    def get_initial(self) -> dict[str, object]:
        initial: dict[str, object] = super().get_initial()
        if self.request.user.is_authenticated:
            initial.setdefault(
                "enrolled_course_set",
                self.request.user.enrolled_course_set.all(),
            )
        return initial

    @override
    def get_form(self, form_class: type[ChangeCoursesForm] | None = None) -> ChangeCoursesForm:
        form: ChangeCoursesForm = super().get_form(form_class)
        enrolled_course_set_field: forms.Field = form.fields["enrolled_course_set"]
        CAN_SET_QUERYSET: Final[bool] = (
            isinstance(enrolled_course_set_field, forms.ModelChoiceField)
            and self.request.user.is_authenticated
        )
        if CAN_SET_QUERYSET:
            university: University | None = self.request.user.university  # type: ignore[union-attr]
            if university:
                enrolled_course_set_field.queryset = university.course_set.all()  # type: ignore[attr-defined]
        return form

    @override
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        if not self.request.user.is_authenticated:
            raise RuntimeError

        submitted_enrolled_course_set: MutableSet[Course | int] = set()

        raw_course: str | Course | int
        # noinspection PyArgumentList
        for raw_course in self.request.POST.getlist("enrolled_course_set"):
            if isinstance(raw_course, Course | int):
                submitted_enrolled_course_set.add(raw_course)
                continue

            try:
                submitted_enrolled_course_set.add(int(raw_course))
            except ValueError:
                pass
            else:
                continue

            submitted_enrolled_course_set.add(Course.objects.get(pk=raw_course))

        self.request.user.enrolled_course_set.set(submitted_enrolled_course_set)

        return django.shortcuts.redirect(self.request.path)


class DeleteAccountView(LoginRequiredMixin, View):
    """The view for processing user post requests to delete their account."""

    http_method_names = ("post",)

    # noinspection PyOverrides
    @override  # type: ignore[misc]
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        user: User | AnonymousUser = self.request.user
        logout(self.request)
        if user.is_authenticated:
            user.delete()
        return django.shortcuts.redirect("default")


class SubmitReportView(LoginRequiredMixin, View):
    """ReportSubmission for handling report submissions."""

    http_method_names = ("post",)

    # noinspection PyOverrides
    @override  # type: ignore[misc]
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        """Take in post-request, Submit to form, Create in the database."""
        form = ReportForm(self.request.POST)

        if form.is_valid():
            report = form.save(commit=False)

            if not self.request.user.is_authenticated:
                raise RuntimeError

            report.reporter = self.request.user

            report.post = Post.objects.get(pk=self.request.POST["post_pk"])
            report.reason = self.request.POST["reason"]
            report.save()

            return django.shortcuts.redirect("ratemymodule:home")

        # Handle invalid form submission
        return django.shortcuts.redirect("ratemymodule:home")
