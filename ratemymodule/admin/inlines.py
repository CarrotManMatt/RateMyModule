"""Custom Django admin inline configuration classes, to display related objects."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "UserMadePostsInline",
    "UserMadeReportsInline",
    "UniversityCoursesInline",
    "ModulePostsInline",
    "PostReportsInline",
)


from django.contrib.admin import StackedInline
from django.utils.translation import gettext_lazy as _
from django_admin_inline_paginator.admin import InlinePaginated, TabularInlinePaginated

from ratemymodule.models import Course, Module, Post, Report, University, User

from .forms import PostModelForm


class UserMadePostsInline(InlinePaginated, StackedInline[Post, User]):  # type: ignore[no-any-unimported,misc]
    """Configuration class to describe how to display Posts inline under a User."""

    classes = ("collapse",)
    extra = 0
    model = Post
    form = PostModelForm
    verbose_name_plural = _("Created Posts")
    fields = (
        "module",
        "content",
        (
            "overall_rating",
            "difficulty_rating",
            "assessment_rating",
            "teaching_rating",
        ),
    )
    autocomplete_fields = ("module",)
    per_page = 10
    template = "admin/partials/stacked_paginated.html"
    pagination_key = "user-made-posts-page"


class UserMadeReportsInline(TabularInlinePaginated[Report, User]):  # type: ignore[no-any-unimported,misc]
    """Configuration class to describe how to display Reports inline under a User."""

    classes = ("collapse",)
    extra = 0
    model = Report
    verbose_name_plural = _("Created Reports")
    fields = (
        "post",
        "reporter",
        "reason",
        "is_solved",
    )
    autocomplete_fields = ("post", "reporter")
    per_page = 10
    pagination_key = "user-made-reports-page"


class UniversityCoursesInline(TabularInlinePaginated[Course, University]):  # type: ignore[no-any-unimported,misc]
    """Configuration class to describe how to display Courses inline under a University."""

    classes = ("collapse",)
    extra = 0
    model = Course
    fields = (
        "name",
        "student_type",
    )
    per_page = 10
    pagination_key = "university-courses-page"


class ModulePostsInline(TabularInlinePaginated[Post, Module]):  # type: ignore[no-any-unimported,misc]
    """Configuration class to describe how to display Posts inline under a Module."""

    classes = ("collapse",)
    extra = 0
    model = Post
    form = PostModelForm
    fields = (
        "user",
        "content",
        (
            "overall_rating",
            "difficulty_rating",
            "assessment_rating",
            "teaching_rating",
        ),
    )
    autocomplete_fields = ("user",)
    per_page = 10
    pagination_key = "module-posts-page"


class PostReportsInline(TabularInlinePaginated[Report, Post]):  # type: ignore[no-any-unimported,misc]
    """Configuration class to describe how to display Reports inline under a Post."""

    classes = ("collapse",)
    extra = 0
    model = Report
    autocomplete_fields = ("reporter",)
    per_page = 10
    pagination_key = "post-reports-page"
