"""Manager classes to create & retrieve instances of models."""

from collections.abc import Sequence

__all__: Sequence[str] = ("UserManager", "UniversityModuleManager", "UserModuleManager")


from typing import TYPE_CHECKING, Final, override

from django.apps import apps
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db.models import Manager, QuerySet

from .utils import AttributeDeleter

if TYPE_CHECKING:
    from . import Module, University, User


class UserManager(DjangoUserManager["User"]):
    """Manager class to create & retrieve instances of the `User` model."""

    normalize_username = AttributeDeleter(
        object_name="UserManager",
        attribute_name="normalize_username"
    )
    use_in_migrations: bool = True

    def _create_user(self, email: str, password: str | None = None, **extra_fields: object) -> "User":  # noqa: E501
        if not email:
            EMPTY_EMAIL_MESSAGE: Final[str] = "Users must have an email address."
            raise ValueError(EMPTY_EMAIL_MESSAGE)

        user: "User" = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    @override
    def create_user(self, email: str | None = None, password: str | None = None, **extra_fields: object) -> "User":  # type: ignore[override] # noqa: E501
        if email is None:
            EMAIL_IS_NONE_MESSAGE: Final[str] = "Email address cannot be `None`."
            raise ValueError(EMAIL_IS_NONE_MESSAGE)

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    @override
    def create_superuser(self, email: str, password: str | None = None, **extra_fields: object) -> "User":  # type: ignore[override] # noqa: E501
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            INVALID_IS_STAFF_MESSAGE: Final[str] = "Superuser must have `is_superuser=True`."
            raise ValueError(INVALID_IS_STAFF_MESSAGE)

        if extra_fields.get("is_superuser") is not True:
            INVALID_IS_SUPERUSER_MESSAGE: Final[str] = (
                "Superuser must have `is_superuser=True`."
            )
            raise ValueError(INVALID_IS_SUPERUSER_MESSAGE)

        return self._create_user(email, password, **extra_fields)


class UniversityModuleManager(Manager["Module"]):
    """
    Manager class to create & retrieve instances of the `Module` model.

    Module objects are selected by the instances that are linked to a university
    through its `course_set`.
    """

    @override
    def __init__(self, university: "University") -> None:
        self.university: University = university
        # noinspection PyTypeChecker
        self.model = apps.get_model(app_label="ratemymodule", model_name="Module")

        super().__init__()

    @override
    def get_queryset(self) -> QuerySet["Module"]:
        return apps.get_model(app_label="ratemymodule", model_name="Module").objects.filter(  # type: ignore[no-any-return]
            course_set__pk__in=self.university.course_set.all()
        ).distinct()


class UserModuleManager(Manager["Module"]):
    """
    Manager class to create & retrieve instances of the `Module` model.

    Module objects are selected by the instances that are linked to a user
    through their `enrolled_course_set`.
    """

    @override
    def __init__(self, user: "User") -> None:
        self._user: User = user
        # noinspection PyTypeChecker
        self.model = apps.get_model(app_label="ratemymodule", model_name="Module")

        super().__init__()

    @override
    def get_queryset(self) -> QuerySet["Module"]:
        return apps.get_model(app_label="ratemymodule", model_name="Module").objects.filter(  # type: ignore[no-any-return]
            course_set__pk__in=self._user.enrolled_course_set.all()
        ).distinct()
