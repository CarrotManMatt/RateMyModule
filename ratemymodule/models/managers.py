"""Manager classes to create & retrieve instances of models."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "UserManager",
    "UniversityModuleManager",
    "UserPossibleModuleManager",
    "PostFilteredByTagManager",
    "ModuleOrRequestVisiblePostsManager",
)


from collections.abc import Iterable
from typing import TYPE_CHECKING, Final, override

from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models import Count, Manager, QuerySet
from django.http import HttpRequest

from .utils import AttributeDeleter

if TYPE_CHECKING:
    from . import Module, Post, University, User


class UserManager(DjangoUserManager["User"]):
    """Manager class to create & retrieve instances of the `User` model."""

    normalize_username = AttributeDeleter(
        object_name="UserManager",
        attribute_name="normalize_username",
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
    def __init__(self, university: "University", module_model: type["Module"]) -> None:
        self._university: University = university
        self._module_model: type["Module"] = module_model

        super().__init__()

    @override
    def get_queryset(self) -> QuerySet["Module"]:
        return self._module_model.objects.filter(
            course_set__pk__in=self._university.course_set.all(),
        ).distinct()


class UserPossibleModuleManager(Manager["Module"]):
    """
    Manager class to create & retrieve instances of the `Module` model.

    Module objects are selected by the instances that could be linked to a user
    through their `enrolled_course_set`.
    """

    @override
    def __init__(self, user: "User", module_model: type["Module"]) -> None:
        self._user: User = user
        self._module_model: type["Module"] = module_model

        super().__init__()

    @override
    def get_queryset(self) -> QuerySet["Module"]:
        return self._module_model.objects.filter(
            course_set__pk__in=self._user.enrolled_course_set.all(),
        ).distinct()


class PostFilteredByTagManager(Manager["Post"]):
    """
    Manager class to create & retrieve instances of the `Post` model.

    Post-objects are selected by whether they have one of the given tags.
    """

    @override
    def __init__(self, tag_names: Iterable[str], post_model: type["Post"]) -> None:
        self._tag_names: Iterable[str] = tag_names
        self._post_model: type["Post"] = post_model

        super().__init__()

    @override
    def get_queryset(self) -> QuerySet["Post"]:
        return self._post_model.objects.filter(
            models.Q(tool_tag_set__name__in=self._tag_names)
            | models.Q(topic_tag_set__name__in=self._tag_names)
            | models.Q(other_tag_set__name__in=self._tag_names)  # noqa: COM812
        ).distinct()


class ModuleOrRequestVisiblePostsManager(Manager["Post"]):
    """Get the posts of a module, filtered by the given request context."""

    @override
    def __init__(self, post_model: type["Post"], module: "Module | None" = None, request: HttpRequest | None = None) -> None:  # noqa: E501
        if not module and not request:
            INVALID_ARGUMENTS_MESSAGE: Final[str] = (
                f"Arguments {"module"!r} and {"request"!r} cannot both be None."
            )
            raise ValueError(INVALID_ARGUMENTS_MESSAGE)

        self._module: "Module | None" = module
        self._request: HttpRequest | None = request
        self._post_model: type["Post"] = post_model

        super().__init__()

    @override
    def get_queryset(self) -> QuerySet["Post"]:
        queryset: QuerySet["Post"] = self._post_model.objects.all()

        if self._module:
            queryset = queryset & self._module.post_set.all()

        if not self._request or not self._request.user.is_staff:
            queryset = queryset.annotate(
                num_reports=Count("report_set"),
            ).annotate(
                num_solved_reports=Count(
                    "report_set",
                    filter=models.Q(report_set__is_solved=True),
                ),
            ).filter(
                hidden=False,
            ).exclude(
                models.Q(num_reports__gt=0) & ~models.Q(num_solved_reports__gt=0),
            )

        return queryset.order_by("date_time_created")
