"""Web HTML views for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "HomeView",
    "SubmitPostView",
    "UserSettingsView",
    "LogoutView",
    "LoginView",
    "SignupView",
    "LikeDislikePostView",
    "ToolTagAutocompleteView",
    "TopicTagAutocompleteView",
    "OtherTagAutocompleteView",
)

import re
from collections.abc import Container
from typing import TYPE_CHECKING, Final, override
from urllib.parse import unquote_plus

import django
from allauth.account.forms import LoginForm
from allauth.account.views import LoginView as AllAuthLoginView
from allauth.account.views import LogoutView as AllAuthLogoutView
from allauth.account.views import SignupView as AllAuthSignupView
from django.conf import settings
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
from django.views.generic import CreateView, TemplateView, View

from ratemymodule.models import (
    Course,
    Module,
    OtherTag,
    Post,
    ToolTag,
    TopicTag,
    University,
)
from web.forms import AnalyticsForm, PostForm, SignupForm

from . import graph_generators

if TYPE_CHECKING:
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


class HomeView(TemplateView):
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

    def _get_advanced_analytics_form_context_data(self, context_data: dict[str, object]) -> dict[str, object]:  # noqa: E501
        if "analytics_form" not in context_data:
            action: str | None = self.request.GET.get("action")

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
                start_year: int = int(self.request.GET.get("aa_start_year"))
                end_year: int = int(self.request.GET.get("aa_end_year"))
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


class SubmitPostView(LoginRequiredMixin, CreateView[Post, PostForm]):
    """SubmitPostView for handling module review submissions."""

    template_name = "ratemymodule/submit-review.html"
    form_class = PostForm
    success_url = "/"  # TODO: change to reverse url lookup
    model = Post
    http_method_names = ("get", "post")

    @override
    def get_form_kwargs(self) -> dict[str, object]:
        kwargs = super().get_form_kwargs()
        if "data" in kwargs:
            data = kwargs["data"].copy()
            for field in ("tool_tags", "topic_tags", "other_tags"):
                if data.get(field):
                    data.setlist(field, data[field].split(","))
            kwargs["data"] = data
        return kwargs

    # noinspection PyOverrides
    @override
    def form_valid(self, form: PostForm) -> HttpResponse:
        self.object = form.save(commit=False)
        if not self.request.user.is_authenticated:  # HACK: Ensure the user is real
            raise RuntimeError
        self.object.user = self.request.user
        self.object.save()

        # Associate tags with the post
        tag_fields = {
            "tool_tags": self.object.tool_tag_set,
            "topic_tags": self.object.topic_tag_set,
            "other_tags": self.object.other_tag_set,
        }

        for field, related_manager in tag_fields.items():
            tag_ids = form.cleaned_data.get(field)
            if tag_ids:
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


class ToolTagAutocompleteView(View):
    """A view for processing get requests for Tool tags."""

    # noinspection PyOverrides
    @override
    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        if "term" in request.GET:
            term = request.GET["term"]
            tags = ToolTag.objects.filter(name__icontains=term).values("id", "name")
            return JsonResponse(list(tags), safe=False)
        return JsonResponse([], safe=False)


class TopicTagAutocompleteView(View):
    """A view for processing get requests about topic tags."""

    # noinspection PyOverrides
    @override
    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        if "term" in request.GET:
            term = request.GET["term"]
            tags = TopicTag.objects.filter(name__icontains=term).values("id", "name")
            return JsonResponse(list(tags), safe=False)
        return JsonResponse([], safe=False)


class OtherTagAutocompleteView(View):
    """A view for processing get requests for other tags."""

    # noinspection PyOverrides
    @override
    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        if "term" in request.GET:
            term = request.GET["term"]
            tags = OtherTag.objects.filter(name__icontains=term).values("id", "name")
            return JsonResponse(list(tags), safe=False)
        return JsonResponse([], safe=False)


class UserSettingsView(LoginRequiredMixin, TemplateView):
    """Account management view, for users to edit their account settings."""

    template_name = "ratemymodule/user-settings.html"
    http_method_names = ("get",)


class LikeDislikePostView(View):
    """View to handle like/dislike of posts."""

    http_method_names = ("post", "get")

    # noinspection PyOverrides
    @override
    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:  # type: ignore[misc]
        post_id = request.POST.get("post_id")
        action = request.POST.get("action")

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

                    # Remove user from opposite set if present
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
