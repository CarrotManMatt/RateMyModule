"""Custom Django admin inline configuration classes, to display related objects."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "UserMadePostsInline",
    "UserMadeReportsInline",
    "UniversityCoursesInline",
    "ModulePostsInline",
    "PostReportsInline",
)


from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ratemymodule.models import Course, Module, Post, Report, University, User

from .forms import PostModelForm


class UserMadePostsInline(admin.StackedInline[Post, User]):
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


class UserMadeReportsInline(admin.TabularInline[Report, User]):
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


class UniversityCoursesInline(admin.TabularInline[Course, University]):
    """Configuration class to describe how to display Courses inline under a University."""

    classes = ("collapse",)
    extra = 0
    model = Course
    fields = (
        "name",
        "student_type",
    )


class ModulePostsInline(admin.TabularInline[Post, Module]):
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


class PostReportsInline(admin.TabularInline[Report, Post]):
    """Configuration class to describe how to display Reports inline under a Post."""

    classes = ("collapse",)
    extra = 0
    model = Report
    autocomplete_fields = ("reporter",)
