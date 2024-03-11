"""Custom filters to show/hide the instances of models within the list admin interface."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "UserIsStaffListFilter",
    "UserGroupListFilter",
    "UserIsActiveListFilter",
    "TagIsVerifiedListFilter",
    "ReportIsSolvedListFilter",
    "ReportReasonListFilter",
    "post_rating_list_filter_builder",
)

from collections.abc import Iterable, MutableMapping
from typing import TypeAlias, final, override

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import Group
from django.db.models import IntegerField, QuerySet
from django.db.models.expressions import Combinable
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import StrOrPromise

from ratemymodule.models import BaseTag, Post, Report, User

RequiredRatingField: TypeAlias = IntegerField[float | int | str | Combinable, int]
OptionalRatingField: TypeAlias = IntegerField[
    float | int | str | Combinable | None,
    int | None  # noqa: COM812
]


class UserIsStaffListFilter(admin.SimpleListFilter):
    """
    Admin filter to limit the `User` objects shown on the admin list view.

    `User` objects are filtered by whether the user is a staff member.
    """

    title = _("Staff Member Status")
    parameter_name = "is_staff"

    @override
    def lookups(self, request: HttpRequest, model_admin: ModelAdmin[User]) -> Iterable[tuple[object, StrOrPromise]] | None:  # type: ignore[override]  # noqa: E501
        return ("1", _("Is Staff Member")), ("0", _("Is Not Staff Member"))

    @override
    def queryset(self, request: HttpRequest, queryset: QuerySet[User]) -> QuerySet[User]:
        if self.value() == "1":
            return queryset.filter(is_staff=True)

        if self.value() == "0":
            return queryset.filter(is_staff=False)

        return queryset


class UserGroupListFilter(admin.SimpleListFilter):
    """
    Admin filter to limit the `User` objects shown on the admin list view.

    `User` objects are filtered by the user's group.
    """

    template = "admin/partials/dropdown_list_filter.html"
    title = _("Group")
    parameter_name = "group"

    @override
    def lookups(self, request: HttpRequest, model_admin: ModelAdmin[User]) -> Iterable[tuple[object, StrOrPromise]] | None:  # type: ignore[override]  # noqa: E501
        return ((str(group.pk), _(str(group.name))) for group in Group.objects.all())

    @override
    def queryset(self, request: HttpRequest, queryset: QuerySet[User]) -> QuerySet[User]:
        group_pk: str | None = self.value()

        if group_pk:
            return queryset.filter(groups=group_pk)

        return queryset


class UserIsActiveListFilter(admin.SimpleListFilter):
    """
    Admin filter to limit the `User` objects shown on the admin list view.

    `User` objects are filtered by whether the user's account is marked as active.
    """

    title = _("Is Active Status")
    parameter_name = "is_active"

    @override
    def lookups(self, request: HttpRequest, model_admin: ModelAdmin[User]) -> Iterable[tuple[object, StrOrPromise]] | None:  # type: ignore[override]  # noqa: E501
        return ("1", _("Is Active")), ("0", _("Is Not Active"))

    @override
    def queryset(self, request: HttpRequest, queryset: QuerySet[User]) -> QuerySet[User]:
        if self.value() == "1":
            return queryset.filter(is_active=True)

        if self.value() == "0":
            return queryset.filter(is_active=False)

        return queryset


class TagIsVerifiedListFilter(admin.SimpleListFilter):
    """
    Admin filter to limit any tag objects shown on the admin list view.

    Tag objects are filtered by whether the tag is verified.
    """

    title = _("Is Verified Status")
    parameter_name = "is_verified"

    @override
    def lookups(self, request: HttpRequest, model_admin: ModelAdmin[BaseTag]) -> Iterable[tuple[object, StrOrPromise]] | None:  # type: ignore[override]  # noqa: E501
        return ("1", _("Is Verified")), ("0", _("Is Not Verified"))

    @override
    def queryset(self, request: HttpRequest, queryset: QuerySet[BaseTag]) -> QuerySet[BaseTag]:
        if self.value() == "1":
            return queryset.filter(is_verified=True)

        if self.value() == "0":
            return queryset.filter(is_verified=False)

        return queryset


class ReportIsSolvedListFilter(admin.SimpleListFilter):
    """
    Admin filter to limit any `Report` objects shown on the admin list view.

    `Report` objects are filtered by whether the report is marked as solved.
    """

    title = _("Is Solved Status")
    parameter_name = "is_solved"

    @override
    def lookups(self, request: HttpRequest, model_admin: ModelAdmin[Report]) -> Iterable[tuple[object, StrOrPromise]] | None:  # type: ignore[override]  # noqa: E501
        return ("1", _("Is Solved")), ("0", _("Is Not Solved"))

    @override
    def queryset(self, request: HttpRequest, queryset: QuerySet[Report]) -> QuerySet[Report]:
        if self.value() == "1":
            return queryset.filter(is_solved=True)

        if self.value() == "0":
            return queryset.filter(is_solved=False)

        return queryset


class ReportReasonListFilter(admin.SimpleListFilter):
    """
    Admin filter to limit the `Report` objects shown on the admin list view.

    `Report` objects are filtered by the report's reason.
    """

    template = "admin/partials/dropdown_list_filter.html"
    title = _("Reason")
    parameter_name = "reason"

    @override
    def lookups(self, request: HttpRequest, model_admin: ModelAdmin[Report]) -> Iterable[tuple[object, StrOrPromise]] | None:  # type: ignore[override]  # noqa: E501
        # noinspection PyUnresolvedReferences
        return ((reason.value, reason.label) for reason in Report.Reasons)

    @override
    def queryset(self, request: HttpRequest, queryset: QuerySet[Report]) -> QuerySet[Report]:
        value: str | None = self.value()
        if value and value in Report.Reasons:
            return queryset.filter(reason=Report.Reasons(value))

        return queryset


def post_rating_list_filter_builder(field: RequiredRatingField | OptionalRatingField) -> type[admin.ListFilter]:  # noqa: E501
    """Create an instance of `admin.ListFilter` to filter Posts by the given rating field."""
    @final
    class _PostRatingListFilter(admin.SimpleListFilter):
        """
        Admin filter to limit any `Post` objects shown on the admin list view.

        `Post` objects are filtered by the given rating.
        """

        template = "admin/partials/dropdown_list_filter.html"
        title = (
            _(field.verbose_name)
            if isinstance(field.verbose_name, str)
            else field.verbose_name
        )
        parameter_name = field.name

        @override
        def lookups(self, request: HttpRequest, model_admin: ModelAdmin[Post]) -> Iterable[tuple[object, StrOrPromise]] | None:  # type: ignore[override]  # noqa: E501
            return ((rating.value, rating.label) for rating in Post.Ratings)

        @override
        def queryset(self, request: HttpRequest, queryset: QuerySet[Post]) -> QuerySet[Post]:
            filter_kwargs: MutableMapping[str, object] = {}

            value: str | None = self.value()
            if value:
                try:
                    casted_value: int = int(value)
                except ValueError:
                    pass
                else:
                    if casted_value in Post.Ratings:
                        filter_kwargs.setdefault(field.name, Post.Ratings(casted_value))

            return queryset.filter(**filter_kwargs)

    return _PostRatingListFilter
