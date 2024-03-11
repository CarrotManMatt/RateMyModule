"""Utility classes & functions used within the admin configuration of this app."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "UnchangeableModelAdmin",
    "CustomBaseModelAdmin",
    "Fieldsets",
    "Fieldset",
)

from collections.abc import Collection
from typing import TYPE_CHECKING, TypeAlias, TypeVar, override

from django.contrib.admin import ModelAdmin
from django.db.models import Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django_stubs_ext import StrPromise

if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from django.contrib.admin.options import _FieldOpts as FieldOpts

ModelT = TypeVar("ModelT", bound=Model)
ChildModelT = TypeVar("ChildModelT", bound=Model)
ParentModelT = TypeVar("ParentModelT", bound=Model)
Fieldset: TypeAlias = tuple[str | StrPromise | None, "FieldOpts"]
Fieldsets: TypeAlias = list[Fieldset] | tuple[Fieldset, ...] | tuple[()]


class CustomBaseModelAdmin(ModelAdmin[ModelT]):
    """
    Base `ModelAdmin` class that provides common configuration for all models.

    Changes made from Django's `ModelAdmin` include:
    * Hiding given fields & fieldsets from displaying
    """

    @override
    def get_fields(self, request: HttpRequest, obj: ModelT | None = None, filter_fields: Collection[str] | None = None) -> Sequence[str | Sequence[str]]:  # noqa: E501
        fields: Sequence[str | Sequence[str]] = super().get_fields(request=request, obj=obj)

        if filter_fields is None:
            filter_fields = ()

        if obj is None:
            fields = (
                [
                    field
                    for field
                    in fields
                    if (
                        isinstance(field, str)
                        and field not in self.get_readonly_fields(request, obj)
                        and field not in filter_fields
                    )
                ]
                + [
                    [
                        inner_field
                        for inner_field
                        in field
                        if (
                            inner_field not in self.get_readonly_fields(request, obj)
                            and field not in filter_fields
                        )
                    ]
                    for field
                    in fields
                    if isinstance(field, Sequence) and not isinstance(field, str)
                ]
            )

        return fields

    @override
    def get_fieldsets(self, request: HttpRequest, obj: ModelT | None = None, filter_fields: Collection[str] | None = None) -> Fieldsets:  # noqa: E501
        fieldsets: Fieldsets = super().get_fieldsets(request=request, obj=obj)

        if filter_fields is None:
            filter_fields = ()

        if obj is None:
            for fieldset in fieldsets:
                fieldset[1]["fields"] = (
                    [
                        field
                        for field
                        in fieldset[1]["fields"]
                        if (
                            isinstance(field, str)
                            and field not in self.get_readonly_fields(request, obj)
                            and field not in filter_fields
                        )
                    ]
                    + [
                        [
                            inner_field
                            for inner_field
                            in field
                            if (
                                inner_field not in self.get_readonly_fields(request, obj)
                                and field not in filter_fields
                            )
                        ]
                        for field
                        in fieldset[1]["fields"]
                        if isinstance(field, Sequence) and not isinstance(field, str)
                    ]
                )

        return fieldsets


class UnchangeableModelAdmin(CustomBaseModelAdmin[ModelT]):
    """Custom `ModelAdmin` configuration class that prevents entering the change view."""

    list_display_links = None

    @override
    def change_view(self, request: HttpRequest, object_id: str, form_url: str = "", extra_context: dict[str, object] | None = None) -> HttpResponse:  # noqa: E501
        # noinspection PyProtectedMember
        return redirect(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist",
        )
