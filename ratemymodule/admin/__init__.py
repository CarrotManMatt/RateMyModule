"""Admin configurations for models in `ratemymodule` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("UserAdmin",)

from typing import TypeAlias, TypeVar, override

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User as DjangoUser
from django.db import models
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateRangeFilterBuilder, DateTimeRangeFilterBuilder

from ratemymodule.models import (
    BaseTag,
    Course,
    Module,
    OtherTag,
    Post,
    Report,
    ToolTag,
    TopicTag,
    University,
    User,
)

from .filters import (
    PostHasSuspiciousUserListFilter,
    ReportIsSolvedListFilter,
    ReportReasonListFilter,
    TagIsVerifiedListFilter,
    UserGroupListFilter,
    UserIsActiveListFilter,
    UserIsStaffListFilter,
    post_rating_list_filter_builder,
)
from .forms import (
    CourseModelForm,
    ModuleModelForm,
    PostModelForm,
    UserChangeForm,
    UserCreationForm,
)
from .inlines import (
    ModulePostsInline,
    PostReportsInline,
    UniversityCoursesInline,
    UserMadePostsInline,
    UserMadeReportsInline,
)
from .utils import CustomBaseModelAdmin, Fieldset, Fieldsets, UnchangeableModelAdmin

T_tag = TypeVar("T_tag", bound=BaseTag)
ReadonlyFieldsList: TypeAlias = list[str] | tuple[str, ...] | tuple[()]

admin.site.site_header = f"RateMyModule {_("Administration")}"
admin.site.site_title = f"RateMyModule {_("Admin")}"
admin.site.index_title = _("Overview")
admin.site.empty_value_display = "- - - - -"

# TODO: Matt: Add admin autocomplete search filtering for many-to-many connections
# TODO: Matt: Make tag "is_verified" true by default on admin site


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Admin display configuration for the `User` model.

    This configuration adds the functionality to provide custom display configurations on the
    list, create & update pages.
    """

    add_form = UserCreationForm
    form = UserChangeForm  # type: ignore[assignment]
    date_hierarchy = "date_time_created"
    filter_horizontal = ("user_permissions",)
    ordering = None
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "is_active",
                    "enrolled_course_set",
                    "university",
                    "made_post_count",
                ),
            }  # noqa: COM812
        ),
        (
            "Authentication",
            {
                "fields": ("date_time_joined", "last_login", "password"),
                "classes": ("collapse",),
            }  # noqa: COM812
        ),
        (
            "Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                    "is_staff",
                    "is_superuser",
                ),
                "classes": ("collapse",),
            }  # noqa: COM812
        ),
        (
            "Liked & Disliked Posts",
            {
                "fields": (
                    ("liked_post_set", "liked_post_count"),
                    ("disliked_post_set", "disliked_post_count"),
                ),
                "classes": ("collapse",),
            }  # noqa: COM812
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    ("password1", "password2"),
                    "enrolled_course_set",
                ),
            }  # noqa: COM812
        ),
        (
            "Extra",
            {
                "fields": ("is_active",),
                "classes": ("collapse",),
            }  # noqa: COM812
        ),
        (
            "Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                    "is_staff",
                    "is_superuser",
                ),
                "classes": ("collapse",),
            }  # noqa: COM812
        ),
    )
    inlines = (UserMadePostsInline, UserMadeReportsInline)
    list_display = (
        "email",
        "is_staff",
        "is_active",
        "made_post_count",
        "last_login",
    )
    list_display_links = ("email",)
    list_editable = (
        "is_staff",
        "is_active",
    )
    list_filter = (
        UserIsStaffListFilter,
        UserGroupListFilter,
        UserIsActiveListFilter,
        ("date_time_created", DateTimeRangeFilterBuilder(title=_("Date & Time Joined"))),
        ("last_login", DateTimeRangeFilterBuilder(title=_("Last Login"))),
    )
    autocomplete_fields = (
        "groups",
        "enrolled_course_set",
        "liked_post_set",
        "disliked_post_set",
    )
    readonly_fields = (
        "email",
        "password",
        "date_time_joined",
        "last_login",
        "university",
        "made_post_count",
        "liked_post_count",
        "disliked_post_count",
    )
    # noinspection SpellCheckingInspection
    search_fields = (
        "email",
        "groups__name",
        "enrolled_course_set__name",
        "enrolled_course_set__student_type",
        "enrolled_course_set__university__name",
        "enrolled_course_set__university__short_name",
        "enrolled_course_set__university__email_domain",
        "made_post_set__module__name",
        "emailaddress__email",
    )
    search_help_text = _(
        "Search for a user's email address, group name, enrolled course name, "
        "student type, posted-about module name, university name, university short name or "
        "university email domain."  # noqa: COM812
    )

    @override
    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:  # type: ignore[override]
        """
        Return a QuerySet of all User model instances that can be edited by the admin site.

        This is used by changelist_view.
        """
        return super().get_queryset(request).annotate(  # type: ignore[return-value]
            made_post_count=models.Count("made_post_set", distinct=True),
            liked_post_count=models.Count("liked_post_set", distinct=True),
            disliked_post_count=models.Count("disliked_post_set", distinct=True),
        )

    @admin.display(description=_("Date & Time Joined"), ordering="date_time_created")
    def date_time_joined(self, obj: User | None) -> str:
        """
        Return the custom formatted string representation of the date_time_joined field.

        This is displayed on the admin page.
        """
        if not obj:
            return admin.site.empty_value_display

        return obj.date_time_joined.strftime("%d %b %Y %I:%M:%S %p")

    @admin.display(description=_("Last Login"), ordering="last_login")
    def last_login(self, obj: User | None) -> str:
        """
        Return the custom formatted string representation of the last_login field.

        This is displayed on the admin page.
        """
        if not obj or not obj.last_login:
            return admin.site.empty_value_display

        return obj.last_login.strftime("%d %b %Y %I:%M:%S %p")

    @admin.display(description=_("University"))
    def university(self, obj: User | None) -> str:
        """
        Return the custom formatted string representation of the university field.

        This is displayed on the admin page.
        """
        if not obj or not obj.university:
            return admin.site.empty_value_display

        return str(obj.university)

    @admin.display(description=_("Number of Created Posts"), ordering="made_post_count")
    def made_post_count(self, obj: User | None) -> int | str:
        """Return the number of posts this user has made, displayed on the admin page."""
        if not obj:
            return admin.site.empty_value_display

        return obj.made_post_count  # type: ignore[attr-defined,no-any-return]

    @admin.display(description=_("Number of Liked Posts"), ordering="liked_post_count")
    def liked_post_count(self, obj: User | None) -> int | str:
        """Return the number of posts this user has liked, displayed on the admin page."""
        if not obj:
            return admin.site.empty_value_display

        return obj.liked_post_count  # type: ignore[attr-defined,no-any-return]

    @admin.display(description=_("Number of Disliked Posts"), ordering="disliked_post_count")
    def disliked_post_count(self, obj: User | None) -> int | str:
        """Return the number of posts this user has made, displayed on the admin page."""
        if not obj:
            return admin.site.empty_value_display

        return obj.disliked_post_count  # type: ignore[attr-defined,no-any-return]

    @override
    def get_fieldsets(self, request: HttpRequest, obj: User | None = None) -> Fieldsets:  # type: ignore[override]
        fieldsets: Fieldsets = super().get_fieldsets(request=request, obj=obj)  # type: ignore[arg-type]

        if obj:
            if not obj.university:
                fieldset: Fieldset
                for fieldset in fieldsets:
                    fieldset[1]["fields"] = (
                        [
                            field
                            for field
                            in fieldset[1]["fields"]
                            if isinstance(field, str) and field != "university"
                        ]
                        + [
                            [
                                inner_field
                                for inner_field
                                in field
                                if inner_field != "university"
                            ]
                            for field
                            in fieldset[1]["fields"]
                            if isinstance(field, Sequence) and not isinstance(field, str)
                        ]
                    )

            elif fieldsets and "university" not in fieldsets[0][1]["fields"]:
                fieldsets[0][1]["fields"] = ["university", *fieldsets[0][1]["fields"]]

        return fieldsets

    @override
    def get_form(self, request: HttpRequest, obj: DjangoUser | None = None, change: bool = False, **kwargs: object) -> type[ModelForm[DjangoUser]]:  # noqa: E501
        kwargs.update(  # NOTE: This changes the labels on the form to remove unnecessary clutter
            {
                "labels": {"password": _("Hashed password string")},
                "help_texts": {
                    "groups": None,
                    "user_permissions": None,
                    "is_staff": None,
                    "is_superuser": None,
                    "is_active": None,
                },
            },
        )
        return super().get_form(request=request, obj=obj, change=change, **kwargs)

    @override
    def get_readonly_fields(self, request: HttpRequest, obj: DjangoUser | None = None) -> ReadonlyFieldsList:  # noqa: E501
        readonly_fields: ReadonlyFieldsList = super().get_readonly_fields(
            request=request,
            obj=obj,
        )

        if request.user.is_superuser:
            readonly_fields = [
                readonly_field
                for readonly_field
                in readonly_fields
                if readonly_field != "email"
            ]

        return readonly_fields

    @override
    def has_add_permission(self, request: HttpRequest) -> bool:
        if not request.user.is_superuser:
            return False

        return super().has_add_permission(request=request)

    @override
    def response_add(self, request: HttpRequest, obj: User | None, post_url_continue: str | None = None) -> HttpResponse:  # type: ignore[override]  # noqa: E501
        return ModelAdmin.response_add(  # type: ignore[misc]
            self=self,
            request=request,
            obj=obj,
            post_url_continue=post_url_continue,
        )


@admin.register(University)
class UniversityAdmin(CustomBaseModelAdmin[University]):
    fields = (
        "name",
        "short_name",
        "email_domain",
        "founding_date",
        "date_time_created",
    )
    list_display = ("name", "short_name", "email_domain", "founding_date")
    list_editable = ("short_name", "email_domain", "founding_date")
    search_fields = ("name", "short_name", "email_domain")
    search_help_text = _("Search for a university's name, short name or email domain")
    readonly_fields = ("date_time_created",)
    list_filter = (
        ("founding_date", DateRangeFilterBuilder(title=_("Founding Date"))),
        (
            "date_time_created",
            DateTimeRangeFilterBuilder(title=_("Date & Time Object Was Created"))  # noqa: COM812
        ),
    )
    inlines = (UniversityCoursesInline,)


@admin.register(Course)
class CourseAdmin(CustomBaseModelAdmin[Course]):
    form = CourseModelForm
    fields = (
        "name",
        "student_type",
        "university",
        "date_time_created",
        "module_set",
        ("enrolled_user_set", "enrolled_user_count"),
    )
    list_display = ("name", "student_type", "university", "enrolled_user_count")
    list_editable = ("student_type", "university")
    search_fields = ("name", "student_type", "university__name")
    search_help_text = _("Search for a course's name, student type or university name")
    readonly_fields = ("date_time_created", "enrolled_user_count")
    autocomplete_fields = ("university",)
    list_filter = (
        (
            "date_time_created",
            DateTimeRangeFilterBuilder(title=_("Date & Time Object Was Created"))  # noqa: COM812
        ),
    )

    @override
    def get_queryset(self, request: HttpRequest) -> QuerySet[Course]:
        """
        Return a QuerySet of all Course model instances that can be edited by the admin site.

        This is used by changelist_view.
        """
        return super().get_queryset(request).annotate(
            enrolled_user_count=models.Count("enrolled_user_set", distinct=True),
        )

    @admin.display(description=_("Number of Users Enrolled"), ordering="enrolled_user_count")
    def enrolled_user_count(self, obj: Module | None) -> int | str:
        """Return the number of users enrolled on this course, displayed on the admin page."""
        if not obj:
            return admin.site.empty_value_display

        return obj.enrolled_user_count  # type: ignore[attr-defined,no-any-return]


@admin.register(Module)
class ModuleAdmin(CustomBaseModelAdmin[Module]):
    form = ModuleModelForm
    fields = ("name", "code", "year_started", "date_time_created", "course_set", "university")
    list_display = ("name", "code", "post_count")
    list_editable = ("code",)
    search_fields = ("name", "code")
    search_help_text = _("Search for a module's name or reference code")
    readonly_fields = ("date_time_created", "university")
    autocomplete_fields = ("course_set",)
    list_filter = (
        ("year_started", DateRangeFilterBuilder(title=_("Date Module Started"))),
        (
            "date_time_created",
            DateTimeRangeFilterBuilder(title=_("Date & Time Object Was Created"))  # noqa: COM812
        ),
    )
    inlines = (ModulePostsInline,)

    @override
    def get_queryset(self, request: HttpRequest) -> QuerySet[Module]:
        """
        Return a QuerySet of all Module model instances that can be edited by the admin site.

        This is used by changelist_view.
        """
        return super().get_queryset(request).annotate(
            post_count=models.Count("post_set", distinct=True),
        )

    @admin.display(description=_("Number of Posts About This Module"), ordering="post_count")
    def post_count(self, obj: Module | None) -> int | str:
        """Return the number of posts about this module, displayed on the admin page."""
        if not obj:
            return admin.site.empty_value_display

        return obj.post_count  # type: ignore[attr-defined,no-any-return]

    @admin.display(description=_("University"))
    def university(self, obj: Module | None) -> str:
        """
        Return the custom formatted string representation of the university field.

        This is displayed on the admin page.
        """
        if not obj:
            return admin.site.empty_value_display

        return str(obj.university)


class BaseTagAdmin(UnchangeableModelAdmin[T_tag]):
    fields = ("name", "post_count", "is_verified", "date_time_created")
    list_display = ("name", "is_verified", "post_count", "date_time_created")
    list_editable = ("name", "is_verified")
    search_fields = ("name",)
    search_help_text = _("Search for a tag's name")
    readonly_fields = ("post_count", "date_time_created")
    list_filter = (
        TagIsVerifiedListFilter,
        (
            "date_time_created",
            DateTimeRangeFilterBuilder(title=_("Date & Time Tag Was Created"))  # noqa: COM812
        ),
    )

    @override
    def get_queryset(self, request: HttpRequest) -> QuerySet[BaseTag]:  # type: ignore[override]
        """
        Return a QuerySet of all tag objects that can be edited by the admin site.

        This is used by changelist_view.
        """
        return super().get_queryset(request).annotate(  # type: ignore[no-any-return]
            post_count=models.Count("post_set", distinct=True),
        )

    @admin.display(description=_("Number of Posts Using this Tag"), ordering="post_count")
    def post_count(self, obj: BaseTag | None) -> int | str:
        """Return the number of posts that include this tag, displayed on the admin page."""
        if not obj:
            return admin.site.empty_value_display

        return obj.post_count  # type: ignore[attr-defined,no-any-return]


@admin.register(ToolTag)
class ToolTagAdmin(BaseTagAdmin[ToolTag]):
    pass


@admin.register(TopicTag)
class TopicTagAdmin(BaseTagAdmin[TopicTag]):
    pass


@admin.register(OtherTag)
class OtherTagAdmin(BaseTagAdmin[OtherTag]):
    pass


@admin.register(Post)
class PostAdmin(CustomBaseModelAdmin[Post]):
    form = PostModelForm
    fieldsets = (
        (None, {"fields": ("user", "module", "content", "academic_year_start")}),
        (
            "Ratings",
            {
                "fields": (
                    "overall_rating",
                    "difficulty_rating",
                    "assessment_rating",
                    "teaching_rating",
                ),
            }  # noqa: COM812
        ),
        (
            "Tags",
            {
                "fields": ("tool_tag_set", "topic_tag_set", "other_tag_set", "tags_count"),
                "classes": ("collapse",),
            }  # noqa: COM812
        ),
        (
            "Likes & Dislikes",
            {
                "fields": (
                    ("liked_user_set", "liked_user_count"),
                    ("disliked_user_set", "disliked_user_count"),
                ),
                "classes": ("collapse",),
            }  # noqa: COM812
        ),
        (
            "Extra",
            {
                "fields": ("date_time_posted", "hidden", "is_user_suspicious"),
                "classes": ("collapse",),
            }  # noqa: COM812
        ),
    )
    list_display = (
        "pk",
        "module",
        "overall_rating",
        "difficulty_rating",
        "assessment_rating",
        "teaching_rating",
        "liked_user_count",
        "disliked_user_count",
    )
    list_editable = (
        "module",
        "overall_rating",
        "difficulty_rating",
        "assessment_rating",
        "teaching_rating",
    )
    autocomplete_fields = (
        "user",
        "module",
        "tool_tag_set",
        "topic_tag_set",
        "other_tag_set",
    )
    search_fields = (
        "user__email",
        "user__groups__name",
        "module__name",
        "content",
        "tags__name",
    )
    search_help_text = _(
        "Search for a post's content, module's name, tag's name, creator's email or "
        "creator's group name",
    )
    list_display_links = ("pk",)
    readonly_fields = (
        "date_time_posted",
        "tags_count",
        "liked_user_count",
        "disliked_user_count",
        "is_user_suspicious",
    )
    # noinspection PyUnresolvedReferences
    list_filter = (
        post_rating_list_filter_builder(Post.overall_rating.field),
        post_rating_list_filter_builder(Post.difficulty_rating.field),
        post_rating_list_filter_builder(Post.assessment_rating.field),
        post_rating_list_filter_builder(Post.teaching_rating.field),
        PostHasSuspiciousUserListFilter,
        ("date_time_created", DateTimeRangeFilterBuilder(title=_("Date & Time Posted"))),
    )
    inlines = (PostReportsInline,)

    @override
    def get_queryset(self, request: HttpRequest) -> QuerySet[Post]:
        """
        Return a QuerySet of all Post model instances that can be edited by the admin site.

        This is used by changelist_view.
        """
        return super().get_queryset(request).annotate(
            tags_count=(
                models.Count("tool_tag_set", distinct=True)
                + models.Count("topic_tag_set", distinct=True)
                + models.Count("other_tag_set", distinct=True)
            ),
            liked_user_count=models.Count("liked_user_set", distinct=True),
            disliked_user_count=models.Count("disliked_user_set", distinct=True),
        )

    @admin.display(description=_("Date & Time Posted"), ordering="date_time_created")
    def date_time_posted(self, obj: Post | None) -> str:
        """
        Return the custom formatted string representation of the date_time_posted field.

        This is displayed on the admin page.
        """
        if not obj:
            return admin.site.empty_value_display

        return obj.date_time_posted.strftime("%d %b %Y %I:%M:%S %p")

    @admin.display(description=_("Number of Tags"), ordering="tags_count")
    def tags_count(self, obj: Post | None) -> int | str:
        """Return the number of tags this post has, to be displayed on the admin page."""
        if not obj:
            return admin.site.empty_value_display

        return obj.tags_count  # type: ignore[attr-defined,no-any-return]

    @admin.display(description=_("Number of Likes"), ordering="liked_user_count")
    def liked_user_count(self, obj: Post | None) -> int | str:
        """Return the number of likes this post has, to be displayed on the admin page."""
        if not obj:
            return admin.site.empty_value_display

        return obj.liked_user_count  # type: ignore[attr-defined,no-any-return]

    @admin.display(description=_("Number of Dislikes"), ordering="disliked_user_count")
    def disliked_user_count(self, obj: Post | None) -> int | str:
        """Return the number of dislikes this post has, to be displayed on the admin page."""
        if not obj:
            return admin.site.empty_value_display

        return obj.disliked_user_count  # type: ignore[attr-defined,no-any-return]

    @admin.display(description=_("Is User Suspicious?"))
    def is_user_suspicious(self, obj: Post | None) -> str:
        if not obj:
            return admin.site.empty_value_display

        return "Yes" if obj.is_user_suspicious else "No"


@admin.register(Report)
class ReportAdmin(CustomBaseModelAdmin[Report]):
    fields = ("post", "reporter", "reason", "is_solved", "date_time_created")
    list_display = ("pk", "post", "reporter", "reason", "is_solved")
    list_editable = ("reason", "is_solved")
    autocomplete_fields = ("post", "reporter")
    search_fields = (
        "post__content",
        "post__module__name",
        "post__tags__name",
        "post__user__email"
        "reporter__email",
    )
    search_help_text = _(
        "Search for a reporter's email or a reported post's content, module name, "
        "tag's name or creator's email"  # noqa: COM812
    )
    list_display_links = ("pk",)
    readonly_fields = ("date_time_created",)
    list_filter = (
        ReportIsSolvedListFilter,
        ReportReasonListFilter,
        ("date_time_created", DateTimeRangeFilterBuilder(title=_("Date & Time Created"))),
    )
