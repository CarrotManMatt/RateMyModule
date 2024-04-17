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
    "LikeDislikePostView",
    "ToolTagAutocompleteView",
    "TopicTagAutocompleteView",
    "OtherTagAutocompleteView",
    "SubmitReportView",
)

import re
from collections.abc import Container, MutableSet
from typing import TYPE_CHECKING, Final, override
from urllib.parse import unquote_plus

import django
from allauth.account.forms import LoginForm
from allauth.account.views import EmailView as AllAuthEmailView
from allauth.account.views import LoginView as AllAuthLoginView
from allauth.account.views import LogoutView as AllAuthLogoutView
from allauth.account.views import PasswordChangeView as AllAuthPasswordChangeView
from allauth.account.views import SignupView as AllAuthSignupView
from django import forms, urls
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
    QueryDict,
)
from django.shortcuts import redirect, render
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

from . import graph_generators
from .utils import EnsureUserHasCoursesMixin

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser
    from django.db.models import QuerySet


class LogoutView(AllAuthLogoutView):  # type: ignore[misc,no-any-unimported]
    """The view for logging out the user."""

    http_method_name = ("post",)


class LoginView(AllAuthLoginView):  # type: ignore[misc,no-any-unimported]
    """The view for processing login requests."""

    http_method_names = ("post",)
    redirect_authenticated_user = True
    prefix = "login"

    @override
    def form_invalid(self, form: LoginForm) -> HttpResponseRedirect:  # type: ignore[misc,no-any-unimported]
        if "login_form" in self.request.session:
            self.request.session.pop("login_form")

        self.request.session["login_form"] = {
            "data": form.data,
            "errors": form.errors,
        }

        return django.shortcuts.redirect(settings.LOGIN_URL)


class SignupView(AllAuthSignupView):  # type: ignore[misc,no-any-unimported]
    """A view for signing up a new user."""

    http_method_names = ("post",)
    redirect_authenticated_user = True
    prefix = "signup"

    @override
    def form_invalid(self, form: SignupForm) -> HttpResponseRedirect:  # type: ignore[misc]
        if "signup_form" in self.request.session:
            self.request.session.pop("signup_form")

        self.request.session["signup_form"] = {
            "data": form.data,
            "errors": form.errors,
        }

        return django.shortcuts.redirect(settings.SIGNUP_URL)


class HomeView(EnsureUserHasCoursesMixin, TemplateView):
    """Main Dashboard view, for users to look at the most recent posts about uni modules."""

    template_name = "ratemymodule/home.html"
    http_method_names = ("get",)

    @override
    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        # noinspection PyArgumentList
        returned_get_params: QueryDict = self.request.GET.copy()

        # noinspection PyTypeChecker
        action: str | None = self.request.GET.get("action", None)

        if action is not None:
            new_action: str = action.strip().replace("-", "_").strip()

            if not new_action:
                returned_get_params.pop("action", None)
                return redirect(f"{self.request.path}?{returned_get_params.urlencode()}")

            if new_action != action:
                returned_get_params["action"] = new_action
                return redirect(f"{self.request.path}?{returned_get_params.urlencode()}")

            ALLOWED_ACTIONS: Final[Container[str]] = (
                "signup",
                "login",
                "select_university",
                "generate_graph",
                "like",
                "dislike",
            )
            if action not in ALLOWED_ACTIONS:
                raise BadRequest

        if action == "signup":
            returned_get_params["action"] = "login"
            return redirect(f"{self.request.path}?{returned_get_params.urlencode()}")

        if action == "select_university":
            if not request.user.is_authenticated:
                # noinspection PyTypeChecker
                raw_university_pk: str | None = self.request.GET.get(
                    "university",
                    None  # noqa: COM812
                )
                if not raw_university_pk:
                    return render(
                        request,
                        "ratemymodule/university-selector.html",
                        {"university_choices": University.objects.all()},
                    )

                try:
                    selected_university: University = University.objects.get(
                        pk=raw_university_pk,
                    )
                except University.DoesNotExist:
                    returned_get_params.pop("university", None)
                    return redirect(f"{self.request.path}?{returned_get_params.urlencode()}")

                self.request.session["selected_university_pk"] = selected_university.pk

            returned_get_params.pop("action", None)
            returned_get_params.pop("university", None)

        # noinspection PyTypeChecker
        module_code: str | None = self.request.GET.get("module", None)
        if not module_code:
            # noinspection PyUnusedLocal
            university: University | None = None

            if self.request.user.is_authenticated:
                university = self.request.user.university

                if not university:
                    raise Course.DoesNotExist

            else:
                try:
                    university = University.objects.get(
                        pk=self.request.session.get("selected_university_pk", None),
                    )
                except University.DoesNotExist:
                    returned_get_params["action"] = "select_university"
                    returned_get_params.pop("university", None)
                    return redirect(f"{self.request.path}?{returned_get_params.urlencode()}")

            if not university:
                raise RuntimeError

            if not university.module_set.exists():
                raise Module.DoesNotExist

            returned_get_params["module"] = university.module_set.all()[0].code

            return redirect(f"{self.request.path}?{returned_get_params.urlencode()}")

        NO_SELECTED_UNIVERSITY: bool = (
            not self.request.user.is_authenticated
            and not self.request.session.get("selected_university_pk", None)
        )
        if NO_SELECTED_UNIVERSITY:
            returned_get_params["action"] = "select_university"
            returned_get_params.pop("university", None)
            return redirect(f"{self.request.path}?{returned_get_params.urlencode()}")

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
                        graph_generators.overall_rating_bar_graph(
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
                        graph_generators.difficulty_rating_bar_graph(
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
                        graph_generators.teaching_quality_bar_graph(
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
                        graph_generators.assessment_quality_bar_graph(
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

        post_set: QuerySet[Post] = Post.filter_by_viewable(module, self.request).all()

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
                return {**context_data, "error": _("Error: Incorrect rating value")}

            post_set = post_set.filter(overall_rating=rating)

        # noinspection PyTypeChecker
        raw_year: str | None = self.request.GET.get("year", None)
        if raw_year:
            try:
                year: int = int(unquote_plus(raw_year))
            except ValueError:
                return {**context_data, "error": _("Error: Incorrect rating value")}

            post_set = post_set.filter(academic_year_start=year)

        return {**context_data, "post_list": post_set}

    def _get_advanced_analytics_form_context_data(self, context_data: dict[str, object]) -> dict[str, object]:  # noqa: E501
        if "analytics_form" not in context_data:
            # noinspection PyTypeChecker
            action: str | None = self.request.GET.get("action", None)

            if action != "generate_graph":
                context_data["analytics_form"] = AnalyticsForm()
            else:
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
                # note: warning for next two lines, should be put in as int, if not int, die
                # noinspection PyTypeChecker
                start_year: int = int(self.request.GET["aa_start_year"])
                # noinspection PyTypeChecker
                end_year: int = int(self.request.GET["aa_end_year"])
                # repopulate form
                context_data["analytics_form"] = AnalyticsForm(
                    initial={
                        "aa_difficulty_rating": difficulty_rating,
                        "aa_teaching_quality": teaching_rating,
                        "aa_assessment_quality": assessment_quality,
                        "aa_overall_rating": overall_rating,
                        "aa_start_year": start_year,
                        "aa_end_year": end_year,
                    },
                )
                # pass data to graph and make it
                # noinspection PyTypeChecker
                context_data["advanced_analytics_graph"] = mark_safe(  # noqa: S308
                    re.sub(
                        "#000002",  # NOTE: defines colour of border of legend box
                        "var(--button-hover)",
                        re.sub(
                            "#000001",  # NOTE: defines color of legend box
                            "var(--secondary-color)",
                            re.sub(
                                "#aaaaaa",
                                "var(--text-color)",
                                graph_generators.advanced_analytics_graph(
                                    module=Module.objects.get(
                                        code=unquote_plus(self.request.GET["module"]),
                                    ),
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
                )

        return context_data

    def _get_login_forms_context_data(self, context_data: dict[str, object]) -> dict[str, object]:  # noqa: E501
        if "login_form" not in context_data:
            if "login_form" not in self.request.session:
                context_data["login_form"] = LoginForm(prefix="login")

            else:
                login_form = LoginForm(
                    data=self.request.session["login_form"]["data"],
                    request=self.request,
                    prefix="login",
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
                    prefix="signup",
                )
                signup_form.is_valid()

                context_data["signup_form"] = signup_form

                self.request.session.pop("signup_form")

        return context_data

    def _get_university_selection_context_data(self, university: University, context_data: dict[str, object]) -> dict[str, object]:  # noqa: E501
        context_data["selected_university"] = university

        # noinspection PyArgumentList
        select_university_get_params: QueryDict = self.request.GET.copy()
        select_university_get_params["action"] = "select_university"

        context_data["select_university_url"] = (
            f"{self.request.path}?{select_university_get_params.urlencode()}"
        )

        return context_data

    @override
    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context_data: dict[str, object] = super().get_context_data(**kwargs)

        # noinspection PyUnusedLocal
        university: University | None = None
        if self.request.user.is_authenticated:
            university = self.request.user.university

            if not university:
                raise Course.DoesNotExist

        else:
            try:
                university = University.objects.get(
                    pk=self.request.session.get("selected_university_pk", None),
                )
            except University.DoesNotExist:
                raise RuntimeError from None

        if not university:
            raise RuntimeError

        context_data["course_list"] = (
            university.course_set.prefetch_related("module_set").all()
        )
        context_data = self._get_university_selection_context_data(university, context_data)

        original_login_path: str
        original_login_seperator: str
        original_login_params: str
        original_login_path, original_login_seperator, original_login_params = (
            settings.LOGIN_URL.partition("?")
        )

        login_url_params: QueryDict = QueryDict("", mutable=True)
        # noinspection PyArgumentList
        login_url_params.update(
            self.request.GET.dict() | QueryDict(original_login_params).dict()  # noqa: COM812
        )
        context_data["LOGIN_URL"] = (
            f"{original_login_path}{original_login_seperator}{login_url_params.urlencode()}"
        )

        context_data = self._get_graphs_context_data(context_data)
        context_data = self._get_post_list_context_data(context_data)
        context_data = self._get_login_forms_context_data(context_data)
        context_data = self._get_advanced_analytics_form_context_data(context_data)

        return context_data  # noqa: RET504


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

    # noinspection PyOverrides
    @override
    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        # noinspection PyTypeChecker
        term = request.GET.get("term", "")
        tags = TopicTag.objects.filter(
            name__icontains=term,
            is_verified=True,
        ).values("id", "name")
        return JsonResponse(list(tags), safe=False)


class ToolTagAutocompleteView(View):
    """A view for processing GET requests for Tool tags."""

    # noinspection PyOverrides
    @override
    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        # noinspection PyTypeChecker
        term = request.GET.get("term", "")
        tags = ToolTag.objects.filter(
            name__icontains=term,
            is_verified=True,
        ).values("id", "name")
        return JsonResponse(list(tags), safe=False)


class OtherTagAutocompleteView(View):
    """A view for processing GET requests for other tags."""

    # noinspection PyOverrides
    @override
    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        # noinspection PyTypeChecker
        term = request.GET.get("term", "")
        tags = OtherTag.objects.filter(
            name__icontains=term,
            is_verified=True,
        ).values("id", "name")
        return JsonResponse(list(tags), safe=False)


class ChangeEmailView(LoginRequiredMixin, AllAuthEmailView):  # type: ignore[misc,no-any-unimported]
    template_name = "ratemymodule/change-email.html"
    http_method_names = ("get", "post")


class ChangePasswordView(LoginRequiredMixin, AllAuthPasswordChangeView):  # type: ignore[misc,no-any-unimported]
    template_name = "ratemymodule/change-password.html"
    http_method_names = ("get", "post")


class ChangeCoursesView(LoginRequiredMixin, FormView[ChangeCoursesForm]):
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
    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if self.request.user.is_authenticated:
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

        return redirect(self.request.path)


class DeleteAccountView(LoginRequiredMixin, View):
    http_method_names = ("post",)

    # noinspection PyOverrides
    @override  # type: ignore[misc]
    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        user: User | AnonymousUser = request.user
        logout(request)
        if user.is_authenticated:
            user.delete()
        return redirect("default")


class LikeDislikePostView(View):
    """View to handle like/dislike of posts."""

    http_method_names = ("post", "get")

    # noinspection PyOverrides
    @override
    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        # noinspection PyTypeChecker
        post_id: str = request.POST["post_id"]
        # noinspection PyTypeChecker
        action: str = request.POST["action"]

        if action in ("like", "dislike") and post_id:
            try:
                post = Post.objects.get(pk=post_id)
                if request.user.is_authenticated:
                    # Check if the user has already liked or disliked the post
                    POST_ALREADY_LIKED: Final[bool] = (
                        post.liked_user_set.filter(pk=request.user.pk).exists()
                        and action == "like"
                    )
                    if POST_ALREADY_LIKED:
                        # User already liked the post, no action needed
                        return JsonResponse(
                            {"message": "User already liked the post"},
                            status=200,
                        )

                    POST_ALREADY_DISLIKED: Final[bool] = (
                        post.disliked_user_set.filter(pk=request.user.pk).exists()
                        and action == "dislike"
                    )
                    if POST_ALREADY_DISLIKED:
                        # User already disliked the post, no action needed
                        return JsonResponse(
                            {"message": "User already disliked the post"},
                            status=200,
                        )

                    # Remove user from the opposite set if it is present
                    if action == "like":
                        post.disliked_user_set.remove(request.user)
                        post.liked_user_set.add(request.user)
                    elif action == "dislike":
                        post.liked_user_set.remove(request.user)
                        post.disliked_user_set.add(request.user)

                    post.save()
                    return JsonResponse(
                        {"message": "Action performed successfully"},
                        status=200,
                    )

                return JsonResponse({"error": "User Not Authenticated"}, status=400)

            except Post.DoesNotExist:
                return JsonResponse({"error": "Post does not exist"}, status=404)

        return JsonResponse({"error": "Invalid Post ID or Action provided"}, status=400)

    # noinspection PyOverrides
    @override
    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        user = request.user
        if user.is_authenticated:
            liked_post_ids = list(user.liked_post_set.values_list("pk", flat=True))
            disliked_post_ids = list(user.disliked_post_set.values_list("pk", flat=True))

            data = {
                "liked_posts": liked_post_ids,
                "disliked_posts": disliked_post_ids,
            }
            return JsonResponse(data)

        return JsonResponse({"error": "User Not Authenticated"})


class SubmitReportView(View):
    """ReportSubmission for handling report submissions."""

    http_method_names = ("post",)

    # noinspection PyOverrides
    @override  # type: ignore[misc]
    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        """Take in post request, Submit to form, Create in database."""
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            if request.user.is_authenticated:
                report.reporter = request.user
            else:
                report.reporter = User.objects.get(pk=1)  #TODO: Charlie: Make it not use an arbitrary user
            report.post = Post.objects.get(pk=request.POST["post_pk"])
            report.reason = request.POST["reason"]
            report.save()
            return HttpResponseRedirect("/")  # Redirect to the desired URL
        # Handle invalid form submission
        return HttpResponseRedirect("/")  # You can redirect to an error page
