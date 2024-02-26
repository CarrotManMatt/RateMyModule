"""Utility classes & functions provided for all models within `ratemymodule` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("AttributeDeleter", "CustomBaseModel")

from collections.abc import Iterable, MutableMapping, MutableSet
from collections.abc import Set as ImmutableSet
from typing import Final, Never, override

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Model
from django.utils.translation import gettext_lazy as _


class AttributeDeleter:
    """Utility class to delete attributes from a parent class (make them inaccessible)."""

    def __init__(self, object_name: str, attribute_name: str) -> None:
        """Assign a given attribute an instance of this class."""
        self.object_name: str = object_name
        self.attribute_name: str = attribute_name

    def __get__(self, instance: object, owner: type) -> Never:
        """Raise an error when accessing this attribute."""
        NO_ATTRIBUTE_MESSAGE: Final[str] = (
            f"type object {self.object_name!r} has no attribute {self.attribute_name!r}"
        )
        raise AttributeError(NO_ATTRIBUTE_MESSAGE)


class CustomBaseModel(Model):
    """
    Base model that provides extra utility methods for all other models to use.

    This class is abstract so should not be instantiated or have a table made for it in
    the database (see https://docs.djangoproject.com/en/4.2/topics/db/models/#abstract-base-classes).
    """

    date_time_created = models.DateTimeField(_("Date & Time Created"), auto_now_add=True)

    class Meta:
        """Metadata options about this model."""

        abstract = True

    @override
    def save(self, *, force_insert: bool = False, force_update: bool = False, using: str | None = None, update_fields: Iterable[str] | None = None) -> None:  # type: ignore[override] # noqa: E501
        self.full_clean()

        super().save(force_insert, force_update, using, update_fields)

    @override
    def __init__(self, *args: object, **kwargs: object) -> None:
        proxy_fields: MutableMapping[str, object] = {
            field_name: kwargs.pop(field_name)
            for field_name
            in set(kwargs.keys()) & self.get_proxy_field_names()
        }

        super().__init__(*args, **kwargs)

        proxy_field_name: str
        value: object
        for proxy_field_name, value in proxy_fields.items():
            setattr(self, proxy_field_name, value)

    def update(self, *, commit: bool = True, force_insert: bool = False, force_update: bool = False, using: str | None = None, update_fields: Iterable[str] | None = None, **kwargs: object) -> None:  # noqa: E501
        """
        Change an in-memory object's values, then save it to the database.

        This simplifies the two steps into a single operation
        (based on Django's Queryset.bulk_update method).

        The 'force_insert' and 'force_update' parameters can be used
        to insist that the "save" must be an SQL insert or update
        (or equivalent for non-SQL backends), respectively.
        Normally, they should not be set.
        """
        unexpected_kwargs: MutableSet[str] = set()

        field_name: str
        for field_name in set(kwargs.keys()) - self.get_proxy_field_names():
            try:
                # noinspection PyUnresolvedReferences
                self._meta.get_field(field_name)
            except FieldDoesNotExist:
                unexpected_kwargs.add(field_name)

        if unexpected_kwargs:
            UNEXPECTED_KWARGS_MESSAGE: Final[str] = (
                f"{self._meta.model.__name__} got unexpected keyword arguments: "
                f"{tuple(unexpected_kwargs)}"
            )
            raise TypeError(UNEXPECTED_KWARGS_MESSAGE)

        value: object
        for field_name, value in kwargs.items():
            setattr(self, field_name, value)

        if commit:
            self.save(
                force_insert=force_insert,
                force_update=force_update,
                using=using,
                update_fields=update_fields
            )

    update.alters_data: bool = True  # type: ignore[attr-defined, misc]

    @classmethod
    def get_proxy_field_names(cls) -> ImmutableSet[str]:
        """
        Return the set of extra names of properties that can be saved to the database.

        These are proxy fields because their values are not stored as object attributes,
        however, they can be used as a reference to a real attribute when saving objects to the
        database.
        """
        return set()
