"""A set of utility functions for RateMyModule."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "NextURLRemovedFromGETParams",
    "EnsureUserHasCoursesMixin",
    "get_reload_with_get_params_url",
    "get_login_url_from_request",
    "get_login_url_with_extra_params",
    "get_signup_url_from_request",
    "get_signup_url_with_extra_params",
)

from typing import Final, NamedTuple, override

from django.conf import settings
from django.http import HttpRequest, HttpResponseBase, QueryDict
from django.shortcuts import redirect
from django.views import View


class NextURLRemovedFromGETParams(NamedTuple):
    next_url: str | None
    returned_get_params: QueryDict


class EnsureUserHasCoursesMixin(View):
    # noinspection PyOverrides
    @override
    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponseBase:  # noqa: E501
        USER_NEEDS_TO_SELECT_COURSE: Final[bool] = (
            self.request.user.is_authenticated
            and not self.request.user.enrolled_course_set.exists()
        )
        if USER_NEEDS_TO_SELECT_COURSE:
            return redirect("ratemymodule:change_courses")

        return super().dispatch(request, *args, **kwargs)


def get_reload_with_get_params_url(request: HttpRequest, get_params: QueryDict) -> str:
    return f"{request.path}?{get_params.urlencode()}" if get_params else request.path


def get_login_url_from_request(request: HttpRequest) -> str:
    # noinspection PyTypeChecker
    return _mix_get_params_from_request_with_url(settings.LOGIN_URL, request.GET)


def get_login_url_with_extra_params(get_params: QueryDict) -> str:
    return _mix_get_params_from_request_with_url(settings.LOGIN_URL, get_params)


def get_signup_url_from_request(request: HttpRequest) -> str:
    # noinspection PyTypeChecker
    return _mix_get_params_from_request_with_url(settings.SIGNUP_URL, request.GET)


def get_signup_url_with_extra_params(get_params: QueryDict) -> str:
    return _mix_get_params_from_request_with_url(settings.SIGNUP_URL, get_params)


def _mix_get_params_from_request_with_url(url: str, get_params: QueryDict) -> str:
    original_login_path: str
    raw_login_url_params: str
    original_login_path, _, raw_login_url_params = url.partition("?")

    login_url_params: QueryDict = QueryDict(raw_login_url_params, mutable=True)

    param_name: str
    for param_name in set(login_url_params.keys()) & set(get_params.keys()):
        login_url_params.setlist(
            param_name,
            [
                param_value
                for param_value
                in get_params.getlist(param_name)
                if param_value not in login_url_params.getlist(param_name)
            ],
        )

    login_url_params.update(get_params)  # type: ignore[arg-type]

    return (
        f"{original_login_path}?{login_url_params.urlencode()}"
        if login_url_params
        else original_login_path
    )
