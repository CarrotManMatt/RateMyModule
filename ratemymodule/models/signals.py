"""Handles signals sent within the `ratemymodule` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("ready",)

from collections.abc import Set
from typing import Final, Literal, TypeAlias

from django import dispatch
from django.db import IntegrityError
from django.db.models import Model, signals

from . import Course, Module, University, User

M2MChangedAction: TypeAlias = (
    Literal["pre_add"]
    | Literal["post_add"]
    | Literal["pre_remove"]
    | Literal["post_remove"]
    | Literal["pre_clear"]
    | Literal["post_clear"]
)


def ready() -> None:
    """Initialise this module when importing & starting signal listeners."""


# noinspection PyUnusedLocal
@dispatch.receiver(signals.m2m_changed, sender=User.enrolled_course_set.through)
def course_removed_from_user(sender: Model, instance: User | Course, action: M2MChangedAction, reverse: bool, model: type[User | Course], pk_set: set[int] | None, **_kwargs: str) -> None:  # noqa: E501, FBT001
    if action not in ("pre_remove", "pre_clear"):
        return

    if not isinstance(instance, User) or reverse or model is not Course:
        return

    if not (isinstance(instance, User) and not reverse and model is Course):
        raise RuntimeError

    ALL_COURSES_REMOVED_FROM_USER: Final[bool] = (
        (
            action == "pre_clear"
            or not instance.enrolled_course_set.exclude(pk__in=pk_set).exists()
        )
        and not instance.is_staff
    )
    if ALL_COURSES_REMOVED_FROM_USER:
        # noinspection PyProtectedMember
        ALL_COURSES_REMOVED_FROM_USER_MESSAGE: Final[str] = (
            f"NOTNULL constraint failed: {sender._meta.model_name} cannot be empty."
        )
        raise IntegrityError(ALL_COURSES_REMOVED_FROM_USER_MESSAGE)


# noinspection PyUnusedLocal
@dispatch.receiver(signals.m2m_changed, sender=Course.enrolled_user_set.through)  # type: ignore[attr-defined]
def user_removed_from_course(sender: Model, instance: Course | User, action: M2MChangedAction, reverse: bool, model: type[Course | User], pk_set: set[int] | None, **_kwargs: str) -> None:  # noqa: E501, FBT001
    if action not in ("pre_remove", "pre_clear"):
        return

    if not isinstance(instance, Course) or not reverse or model is not User:
        return

    if not (isinstance(instance, Course) and reverse and model is User):
        raise RuntimeError

    ALL_COURSES_REMOVED_FROM_USER: Final[bool] = any(
        (
            not to_be_removed_enrolled_user.is_staff
            and (
                not to_be_removed_enrolled_user.enrolled_course_set.exclude(
                    pk=instance.pk,
                ).exists()
            )
        )
        for to_be_removed_enrolled_user
        in (
            instance.enrolled_user_set.all()
            if action == "pre_clear"
            else User.objects.filter(pk__in=pk_set)
        )
    )
    if ALL_COURSES_REMOVED_FROM_USER:
        # noinspection PyProtectedMember
        ALL_COURSES_REMOVED_FROM_USER_MESSAGE: Final[str] = (
            f"NOTNULL constraint failed: {sender._meta.model_name} cannot be empty."
        )
        raise IntegrityError(ALL_COURSES_REMOVED_FROM_USER_MESSAGE)


# noinspection PyUnusedLocal
@dispatch.receiver(signals.m2m_changed, sender=Module.course_set.through)
def course_removed_from_module(sender: Model, instance: Module | Course, action: M2MChangedAction, reverse: bool, model: type[Module | Course], pk_set: set[int] | None, **_kwargs: str) -> None:  # noqa: E501, FBT001
    if action not in ("pre_remove", "pre_clear"):
        return

    if not isinstance(instance, Module) or reverse or model is not Course:
        return

    if not (isinstance(instance, Module) and not reverse and model is Course):
        raise RuntimeError

    ALL_COURSES_REMOVED_FROM_MODULE: Final[bool] = (
        action == "pre_clear"
        or not instance.course_set.exclude(pk__in=pk_set).exists()
    )
    if ALL_COURSES_REMOVED_FROM_MODULE:
        # noinspection PyProtectedMember
        ALL_COURSES_REMOVED_FROM_MODULE_MESSAGE: Final[str] = (
            f"NOTNULL constraint failed: {sender._meta.model_name} cannot be empty."
        )
        raise IntegrityError(ALL_COURSES_REMOVED_FROM_MODULE_MESSAGE)


# noinspection PyUnusedLocal
@dispatch.receiver(signals.m2m_changed, sender=Course.module_set.through)  # type: ignore[attr-defined]
def module_removed_from_course(sender: Model, instance: Course | Module, action: M2MChangedAction, reverse: bool, model: type[Course | Module], pk_set: set[int] | None, **_kwargs: str) -> None:  # noqa: E501, FBT001
    if action not in ("pre_remove", "pre_clear"):
        return

    if not isinstance(instance, Course) or not reverse or model is not Module:
        return

    if not (isinstance(instance, Course) and reverse and model is Module):
        raise RuntimeError

    ALL_COURSES_REMOVED_FROM_MODULE: Final[bool] = any(
        not to_be_removed_module.course_set.exclude(pk=instance.pk).exists()
        for to_be_removed_module
        in (
            instance.module_set.all()
            if action == "pre_clear"
            else Module.objects.filter(pk__in=pk_set)
        )
    )
    if ALL_COURSES_REMOVED_FROM_MODULE:
        # noinspection PyProtectedMember
        ALL_COURSES_REMOVED_FROM_MODULE_MESSAGE: Final[str] = (
            f"NOTNULL constraint failed: {sender._meta.model_name} cannot be empty."
        )
        raise IntegrityError(ALL_COURSES_REMOVED_FROM_MODULE_MESSAGE)


# noinspection PyUnusedLocal
@dispatch.receiver(signals.m2m_changed, sender=User.enrolled_course_set.through)
def course_added_to_user(sender: Model, instance: User | Course, action: M2MChangedAction, reverse: bool, model: type[User | Course], pk_set: set[int] | None, **_kwargs: str) -> None:  # noqa: E501, FBT001, ARG001
    if action != "pre_add":
        return

    if not isinstance(instance, User) or reverse or model is not Course:
        return

    if not (isinstance(instance, User) and not reverse and model is Course):
        raise RuntimeError

    user_university: University | None = instance.university
    if not user_university:
        raise RuntimeError

    if Course.objects.filter(pk__in=pk_set).exclude(university=user_university).exists():
        # noinspection PyProtectedMember
        USER_ENROLLED_IN_MULTIPLE_UNIVERSITIES_MESSAGE: Final[str] = (
            "VALIDATION constraint failed: "
            f"{instance._meta.model_name} cannot be enrolled in "
            f"{
                model._meta.verbose_name_plural.lower()
                if model._meta.verbose_name_plural
                else "courses"
            } across multiple universities."
        )
        raise IntegrityError(USER_ENROLLED_IN_MULTIPLE_UNIVERSITIES_MESSAGE)


# noinspection PyUnusedLocal
@dispatch.receiver(signals.m2m_changed, sender=Course.enrolled_user_set.through)  # type: ignore[attr-defined]
def user_added_to_course(sender: Model, instance: Course | User, action: M2MChangedAction, reverse: bool, model: type[Course | User], pk_set: set[int] | None, **_kwargs: str) -> None:  # noqa: E501, FBT001, ARG001
    if action != "pre_add":
        return

    if not isinstance(instance, Course) or not reverse or model is not User:
        return

    if not (isinstance(instance, Course) and reverse and model is User):
        raise RuntimeError

    # noinspection PyProtectedMember
    COURSE_IS_NOT_AT_USERS_UNIVERSITY_MESSAGE: Final[str] = (
        "VALIDATION constraint failed: "
        f"{model._meta.model_name} cannot be enrolled in "
        f"{
            instance._meta.verbose_name_plural.lower()
            if instance._meta.verbose_name_plural
            else "courses"
        } across multiple universities."
    )

    ADDED_USERS_ARE_NOT_AT_COURSES_UNIVERSITY: Final[bool] = any(
        (user.university and user.university != instance.university)
        for user
        in User.objects.filter(pk__in=pk_set)
    )
    if ADDED_USERS_ARE_NOT_AT_COURSES_UNIVERSITY:
        raise IntegrityError(COURSE_IS_NOT_AT_USERS_UNIVERSITY_MESSAGE)


def _get_module_university_from_course_pk(course_pk_set: Set[int]) -> University:
    if not course_pk_set:
        raise Course.DoesNotExist

    mutable_course_pk_set: set[int] = set(course_pk_set).copy()

    try:
        return Course.objects.get(pk=mutable_course_pk_set.pop()).university
    except Course.DoesNotExist:
        return _get_module_university_from_course_pk(mutable_course_pk_set)


# noinspection PyUnusedLocal
@dispatch.receiver(signals.m2m_changed, sender=Module.course_set.through)
def course_added_to_module(sender: Model, instance: Module | Course, action: M2MChangedAction, reverse: bool, model: type[Module | Course], pk_set: set[int] | None, **_kwargs: str) -> None:  # noqa: E501, FBT001, ARG001
    if action != "pre_add":
        return

    if not isinstance(instance, Module) or reverse or model is not Course:
        return

    if not (isinstance(instance, Module) and not reverse and model is Course):
        raise RuntimeError

    try:
        module_university: University = instance.university
    except Course.DoesNotExist:
        if pk_set is None:
            raise Course.DoesNotExist from None

        module_university = _get_module_university_from_course_pk(pk_set)

    if Course.objects.filter(pk__in=pk_set).exclude(university=module_university).exists():
        # noinspection PyProtectedMember
        MODULE_ATTACHED_TO_MULTIPLE_UNIVERSITIES_MESSAGE: Final[str] = (
            "VALIDATION constraint failed: "
            f"{instance._meta.model_name} cannot be attached to "
            f"{
                model._meta.verbose_name_plural.lower()
                if model._meta.verbose_name_plural
                else "courses"
            } across multiple universities."
        )
        raise IntegrityError(MODULE_ATTACHED_TO_MULTIPLE_UNIVERSITIES_MESSAGE)

# DONE: Signal to prevent deleting all courses from user (if they are not staff)
# DONE: Signal to prevent deleting user from course if it would make their enrolled_course_set empty (if they are not staff)
# DONE: Signal to prevent deleting all courses from module
# DONE: Signal to prevent deleting module from course if it would make module's course_set empty
# DONE: Signal to ensure course added to user's enrolled_course_set are at same university
# DONE: Signal to ensure user added to course's enrolled_user_set are at same university
# DONE: Signal to ensure course added to module's course_set are at same university
# TODO: Matt: Signal to ensure module added to course's module_set are at same university
# TODO: Matt: Signal to ensure module added to course's module_set does not have same name as any other module in course's university
# TODO: Matt: Signal to ensure module added to course's module_set does not have same code as any other module in course's university
# TODO: Matt: Signal to ensure course added to module's course_set does not have a module at it's university with the same name
# TODO: Matt: Signal to ensure course added to module's course_set does not have a module at it's university with the same code
# TODO: Matt: Signal to prevent removing course from module or from user if there is a post forcing a link
# TODO: Matt: Signal to prevent removing module or user from course if there is a post forcing a link
# TODO: Matt: Signal to remove post dislike when added to a user's liked_post_set
# TODO: Matt: Signal to remove post like when added to a user's disliked_post_set
# TODO: Matt: Signal to remove user from disliked_user_set when added to post's liked_user_set
# TODO: Matt: Signal to remove user from liked_user_set when added to post's disliked_user_set
# TODO: Matt: Signal to prevent removing post from creator's liked_post_set
# TODO: Matt: Signal to prevent removing creator from post's liked_user_set
# TODO: Matt: Signal to prevent adding post creator to creator's disliked_post_set
# TODO: Matt: Signal to prevent adding creator to post's disliked_user_set
