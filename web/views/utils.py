from collections.abc import Sequence

__all__: Sequence[str] = ("EnsureUserHasCoursesMixin",)

from typing import Final, override

from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import redirect
from django.views import View


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
