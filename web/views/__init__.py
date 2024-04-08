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
from allauth.account.forms import LoginForm
from allauth.account.views import LoginView as AllAuthLoginView
from allauth.account.views import LogoutView as AllAuthLogoutView
from allauth.account.views import SignupView as AllAuthSignupView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, \
    QueryDict, JsonResponse
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, View

from django.db.models import Count, Q

from ratemymodule.models import Module, Post, University, User, TopicTag, \
    ToolTag, OtherTag
from web.forms import PostForm, SignupForm
from web.views import graph_utils

if TYPE_CHECKING:
    from django.db.models import QuerySet


class LogoutView(AllAuthLogoutView):  # type: ignore[misc,no-any-unimported]
    http_method_name = ("post",)


class LoginView(AllAuthLoginView):  # type: ignore[misc,no-any-unimported]
    http_method_names = ("post",)
    redirect_authenticated_user = True
    prefix = "login"

    @override
    def form_invalid(self,
                     form: LoginForm) -> HttpResponseRedirect:  # type: ignore[misc,no-any-unimported]
        if "login_form" in self.request.session:
            self.request.session.pop("login_form")

        self.request.session["login_form"] = {
            "data": form.data,
            "errors": form.errors,
        }

        return django.shortcuts.redirect(settings.LOGIN_URL)


class SignupView(AllAuthSignupView):  # type: ignore[misc,no-any-unimported]
    http_method_names = ("post",)
    redirect_authenticated_user = True
    prefix = "signup"

    @override
    def form_invalid(self,
                     form: SignupForm) -> HttpResponseRedirect:  # type: ignore[misc]
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
    def get(self, request: HttpRequest, *args: object,
            **kwargs: object) -> HttpResponse:
        # noinspection PyArgumentList
        signup_action: str | None = self.request.GET.get("action")
        if signup_action == "signup":
            # noinspection PyArgumentList
            signup_get_params: QueryDict = self.request.GET.copy()
            signup_get_params["action"] = "login"
            return redirect(
                f"{self.request.path}?{signup_get_params.urlencode()}")

        # noinspection PyArgumentList
        module_code: str | None = self.request.GET.get("module")
        if module_code is None:
            university: University = (
                self.request.user.university
                if self.request.user.is_authenticated and self.request.user.university
                else University.objects.get(
                    name="The University of Birmingham")
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
    def _get_graphs_context_data(self, context_data: dict[str, object]) -> \
            dict[str, object]:
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
            module: Module = Module.objects.get(
                code=unquote_plus(self.request.GET["module"]))
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

    def _get_post_list_context_data(self, context_data: dict[str, object]) -> \
            dict[str, object]:  # noqa: E501
        try:
            # noinspection PyTypeChecker
            module: Module = Module.objects.get(
                code=unquote_plus(self.request.GET["module"]))
        except Module.DoesNotExist:
            return {**context_data, "error": _("Error: Module Not Found")}

        post_set: QuerySet[Post] = module.post_set.annotate(
            num_reports=Count('report_set')
        ).annotate(
            num_solved_reports=Count('report_set', filter=Q(report_set__is_solved=True))
        ).filter(
            hidden=False
        ).exclude(
            Q(num_reports__gt=0) & ~Q(num_solved_reports__gt=0)
        ).order_by("date_time_created")

        # noinspection PyArgumentList
        raw_search_string: str | None = self.request.GET.get("q")
        if raw_search_string:
            post_set = post_set.filter(
                content__icontains=unquote_plus(raw_search_string))

        # noinspection PyArgumentList
        raw_rating: str | None = self.request.GET.get("rating")
        if raw_rating:
            try:
                rating: Post.Ratings = Post.Ratings(
                    int(unquote_plus(raw_rating)))
            except ValueError:
                return {**context_data,
                        "error": _("Error: Incorrect rating value")}

            post_set = post_set.filter(overall_rating=rating)

        # noinspection PyArgumentList
        raw_year: str | None = self.request.GET.get("year")
        if raw_year:
            try:
                year: int = int(unquote_plus(raw_year))
            except ValueError:
                return {**context_data,
                        "error": _("Error: Incorrect rating value")}

            post_set = post_set.filter(academic_year_start=year)

        return {**context_data, "post_list": post_set}

    def _get_login_forms_context_data(self, context_data: dict[str, object]) -> \
            dict[str, object]:  # noqa: E501
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

    @override
    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context_data: dict[str, object] = super().get_context_data(**kwargs)

        context_data["course_list"] = (
            (
                self.request.user.university
                if self.request.user.is_authenticated and self.request.user.university
                else University.objects.get(
                    name="The University of Birmingham")
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
    http_method_names = ("get", "post")

    @override
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'data' in kwargs:
            data = kwargs['data'].copy()
            for field in ('tool_tags', 'topic_tags', 'other_tags'):
                if field in data and data[field]:
                    data.setlist(field, data[field].split(','))
            kwargs['data'] = data
        return kwargs

    # noinspection PyOverrides
    @override
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        # Associate tags with the post
        tag_fields = {
            'tool_tags': self.object.tool_tag_set,
            'topic_tags': self.object.topic_tag_set,
            'other_tags': self.object.other_tag_set,
        }

        for field, related_manager in tag_fields.items():
            tag_ids = form.cleaned_data.get(field)
            if tag_ids:
                related_manager.set(
                    tag_ids)

        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    # noinspection PyOverrides
    @override
    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context["module_choices"] = Module.objects.all()
        context["academic_year_choices"] = (
            self.form_class.ACADEMIC_YEAR_CHOICES
        )
        return context


class TopicTagAutocompleteView(View):
    def get(self, request):
        if 'term' in request.GET:
            term = request.GET['term']
            tags = TopicTag.objects.filter(name__icontains=term).values('id',
                                                                        'name')
            return JsonResponse(list(tags), safe=False)
        return JsonResponse([], safe=False)


class ToolTagAutocompleteView(View):
    def get(self, request):
        if 'term' in request.GET:
            term = request.GET['term']
            tags = ToolTag.objects.filter(name__icontains=term).values('id',
                                                                       'name')
            return JsonResponse(list(tags), safe=False)
        return JsonResponse([], safe=False)


class OtherTagAutocompleteView(View):
    def get(self, request):
        if 'term' in request.GET:
            term = request.GET['term']
            tags = OtherTag.objects.filter(name__icontains=term).values('id',
                                                                        'name')
            return JsonResponse(list(tags), safe=False)
        return JsonResponse([], safe=False)


class UserSettingsView(LoginRequiredMixin, TemplateView):
    """Account management view, for users to edit their account settings."""

    template_name = "ratemymodule/user-settings.html"
    http_method_names = ("get",)


class LikeDislikePostView(View):
    """View to handle like/dislike of posts"""

    http_method_names = ("post", "get",)

    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        action = request.POST.get('action')

        if post_id and action in ["like", "dislike"]:
            try:
                post = Post.objects.get(pk=post_id)
                if request.user.is_authenticated:
                    # Check if the user has already liked or disliked the post
                    if post.liked_user_set.filter(pk=request.user.pk).exists() and action == "like":
                        # User already liked the post, no action needed
                        return JsonResponse({'message': 'User already liked the post'}, status=200)
                    elif post.disliked_user_set.filter(pk=request.user.pk).exists() and action == "dislike":
                        # User already disliked the post, no action needed
                        return JsonResponse({'message': 'User already disliked the post'}, status=200)

                    # Remove user from opposite set if present
                    if action == "like":
                        post.disliked_user_set.remove(request.user)
                        post.liked_user_set.add(request.user)
                    elif action == "dislike":
                        post.liked_user_set.remove(request.user)
                        post.disliked_user_set.add(request.user)

                    post.save()
                    return JsonResponse({'message': 'Action performed successfully'}, status=200)
                else:
                    return JsonResponse({'error': 'User Not Authenticated'}, status=400)
            except Post.DoesNotExist:
                return JsonResponse({'error': 'Post does not exist'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid Post ID or Action provided'}, status=400)

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            liked_post_ids = list(user.liked_post_set.values_list('pk', flat=True))
            disliked_post_ids = list(user.disliked_post_set.values_list('pk', flat=True))

            data = {
                'liked_posts': liked_post_ids,
                'disliked_posts': disliked_post_ids
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'User Not Authenticated'})
