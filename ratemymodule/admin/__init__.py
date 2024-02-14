"""Admin configurations for models in `ratemymodule` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("UserAdmin",)

from typing import TypeAlias, override

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User as DjangoUser
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from ratemymodule.models import User

from .forms import UserChangeForm

ReadonlyFieldsList: TypeAlias = list[str] | tuple[str, ...] | tuple[()]


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Admin display configuration for the :model:`ratemymodule.user` model.

    This configuration adds the functionality to provide custom display configurations on the
    list, create & update pages.
    """

    form = UserChangeForm  # type: ignore[assignment]
    date_hierarchy = "date_time_created"
    filter_horizontal = ("user_permissions",)
    ordering = ("email",)
    fieldsets = (
        (None, {
            "fields": (
                "email",
                "is_active",
                # "enrolled_course_set"
            )
        }),
        ("Authentication", {
            "fields": ("date_time_joined", "last_login", "password"),
            "classes": ("collapse",)
        }),
        ("Permissions", {
            "fields": (
                "groups",
                "user_permissions",
                "is_staff",
                "is_superuser"
            ),
            "classes": ("collapse",)
        })
    )
    add_fieldsets = (
        (None, {
            "fields": (
                "email",
                ("password1", "password2")
            )
        }),
        ("Extra", {
            "fields": ("is_active",),
            "classes": ("collapse",)
        }),
        ("Permissions", {
            "fields": (
                "groups",
                "user_permissions",
                "is_staff",
                "is_superuser"
            ),
            "classes": ("collapse",)
        })
    )
    # inlines = (UserAuthTokensInline,)
    list_display = (
        "email",
        "is_staff",
        "is_active"
    )
    list_display_links = ("email",)
    list_editable = (
        "is_staff",
        "is_active"
    )
    # list_filter = (
    #     UserIsStaffListFilter,
    #     UserGroupListFilter,
    #     UserIsActiveListFilter,
    #     ("date_joined", DateTimeRangeFilterBuilder(title=_("Date Joined"))),
    #     ("last_login", DateTimeRangeFilterBuilder(title=_("Last Login")))
    # )
    autocomplete_fields = ("groups",)
    readonly_fields = (
        "email",
        "password",
        "date_time_joined",
        "last_login"
    )
    search_fields = ("email",)
    search_help_text = _("Search for a user's email address")

    @admin.display(description="Date Joined", ordering="date_time_joined")
    def date_time_joined(self, obj: User | None) -> str:
        """
        Return the custom formatted string representation of the date_time_joined field.

        This is displayed on the admin page.
        """
        if not obj:
            return admin.site.empty_value_display

        return obj.date_time_joined.strftime("%d %b %Y %I:%M:%S %p")

    @admin.display(description="Last Login", ordering="last_login")
    def last_login(self, obj: User | None) -> str:
        """
        Return the custom formatted string representation of the last_login field.

        This is displayed on the admin page.
        """
        if not obj or not obj.last_login:
            return admin.site.empty_value_display

        return obj.last_login.strftime("%d %b %Y %I:%M:%S %p")

    @override
    def get_form(self, request: HttpRequest, obj: DjangoUser | None = None, change: bool = False, **kwargs: object) -> type[ModelForm[DjangoUser]]:  # noqa: E501
        kwargs.update(  # NOTE: Change the labels on the form to remove unnecessary clutter
            {
                "labels": {"password": _("Hashed password string")},
                "help_texts": {
                    "groups": None,
                    "user_permissions": None,
                    "is_staff": None,
                    "is_superuser": None,
                    "is_active": None
                }
            }
        )
        return super().get_form(request=request, obj=obj, change=change, **kwargs)

    @override
    def get_readonly_fields(self, request: HttpRequest, obj: DjangoUser | None = None) -> ReadonlyFieldsList:  # noqa: E501
        readonly_fields: ReadonlyFieldsList = super().get_readonly_fields(
            request=request,
            obj=obj
        )

        if request.user.is_superuser:
            readonly_fields = [
                readonly_field
                for readonly_field
                in readonly_fields
                if readonly_field != "email"
            ]

        return readonly_fields
