from collections.abc import Sequence

__all__: Sequence[str] = ("TestCase", "TestDataGenerator")

import functools
import itertools
import json
from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import AbstractContextManager

# noinspection PyProtectedMember
from contextlib import _GeneratorContextManager as GeneratorContextManager
from types import TracebackType
from typing import IO, Final, Protocol, Self, override

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase as DjangoTestCase
from django.utils import timezone

from ratemymodule.exceptions import NotEnoughTestDataError
from ratemymodule.models import Course, Module, University, User
from ratemymodule.models.managers import UserManager


class _SubTestCallable(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> AbstractContextManager[None]:
        pass


class _SubTestWrapperFuncCallable(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> Iterator[None]:
        pass


def _load_test_data() -> Mapping[str, Mapping[str, Iterable[object]]]:
    if not settings.TEST_DATA_JSON_FILE_PATH:
        EMPTY_TEST_DATA_JSON_FILE_PATH: Final[str] = (
            "TEST_DATA_JSON_FILE_PATH cannot be empty."
        )
        raise ValueError(EMPTY_TEST_DATA_JSON_FILE_PATH)

    test_data_json_file: IO[str]
    with settings.TEST_DATA_JSON_FILE_PATH.open("rt") as test_data_json_file:
        return json.load(test_data_json_file)  # type: ignore[no-any-return]


_TEST_DATA: Final[Mapping[str, Mapping[str, Iterable[object]]]] = (
    _load_test_data() if settings.TEST_DATA_JSON_FILE_PATH else {}
)
if not _TEST_DATA:
    EMPTY_TEST_DATA_JSON_FILE_PATH_MESSAGE: Final[str] = (
        "TEST_DATA_JSON_FILE_PATH cannot be empty when running tests."
    )
    raise ImproperlyConfigured(EMPTY_TEST_DATA_JSON_FILE_PATH_MESSAGE)


class _TestDataWrapper:
    ORIGINAL_TEST_DATA: Final[Mapping[str, Mapping[str, Iterable[object] | Callable[[], Iterator[object]]]]] = {  # noqa: E501
        "user": {"email_local": set(_TEST_DATA["user"]["email_local"])},
        "university": {
            "name": set(_TEST_DATA["university"]["name"]),
            "short_name": set(_TEST_DATA["university"]["short_name"]),
            "email_domain": set(_TEST_DATA["university"]["email_domain"]),
        },
        "course": {
            "name": set(_TEST_DATA["course"]["name"]),
            "student_type": set(_TEST_DATA["course"]["student_type"]),
        },
        "module": {
            "name": set(_TEST_DATA["module"]["name"]),
            "code": lambda: (f"000{count}" for count in itertools.count(start=1)),
        },
        "tool_tag": {
            "name": set(_TEST_DATA["tool_tag"]["name"]),
        },
        "topic_tag": {
            "name": set(_TEST_DATA["topic_tag"]["name"]),
        },
        "other_tag": {
            "name": set(_TEST_DATA["other_tag"]["name"]),
        },
        "post": {
            "content": set(_TEST_DATA["post"]["content"]),
        },
    }

    @override
    def __init__(self, test_data_iterators: dict[str, dict[str, Iterator[object]]] | None = None) -> None:  # noqa: E501
        self._test_data_iterators: dict[str, dict[str, Iterator[object]]] = (
            test_data_iterators
            if test_data_iterators is not None
            else {
                model_name: {
                    field_name: (
                        iter(field_test_data)
                        if isinstance(field_test_data, Iterable)
                        else field_test_data()
                    )
                    for field_name, field_test_data
                    in model_test_data.items()
                }
                for model_name, model_test_data
                in self.ORIGINAL_TEST_DATA.items()
            }
        )

    def __getitem__(self, item: str) -> dict[str, Iterator[object]]:
        return self._test_data_iterators[item]

    def _copy_iterator(self, model_name: str, field_name: str) -> Iterator[object]:
        new_original_iterator: Iterator[object]
        copied_iterator: Iterator[object]
        new_original_iterator, copied_iterator = itertools.tee(
            self._test_data_iterators[model_name][field_name],
            2,
        )

        self._test_data_iterators[model_name][field_name] = new_original_iterator

        return copied_iterator

    def __copy__(self) -> Self:
        return type(self)(
            test_data_iterators={
                model_name: {
                    field_name: self._copy_iterator(model_name, field_name)
                    for field_name
                    in model_test_data
                }
                for model_name, model_test_data
                in self._test_data_iterators.items()
            },
        )

    def copy(self) -> Self:
        return self.__copy__()


class TestDataGenerator:
    _test_data_iterators: _TestDataWrapper

    @classmethod
    def create_user_email(cls, *, with_new_university: bool = False) -> str:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a user email because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        test_data_iterator_error: StopIteration
        try:
            created_email_local: object = next(cls._test_data_iterators["user"]["email_local"])
        except StopIteration as test_data_iterator_error:
            raise NotEnoughTestDataError(
                model_name="user",
                field_name="email_local",
            ) from test_data_iterator_error

        if not isinstance(created_email_local, str):
            INVALID_TEST_DATA_TYPE_MESSAGE: Final[str] = "email_local must be a string."
            raise TypeError(INVALID_TEST_DATA_TYPE_MESSAGE)

        if not with_new_university and not University.objects.exists():
            cls.create_university()

        university: University = (
            cls.create_university()
            if with_new_university
            else University.objects.all()[0]
        )

        return f"{created_email_local}@{university.email_domain}"

    @classmethod
    def create_user(cls, *, save: bool = True) -> User:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a User because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        previous_test_data_iterators: _TestDataWrapper = cls._test_data_iterators.copy()

        try:
            if save:
                return User.objects.create_user(email=cls.create_user_email())

            created_user: User = User(
                email=UserManager.normalize_email(cls.create_user_email()),
            )
            created_user.set_password(None)

        except (ValidationError, IntegrityError):
            cls._test_data_iterators = previous_test_data_iterators
            raise

        return created_user

    @classmethod
    def create_university_name(cls) -> str:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a university name because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        test_data_iterator_error: StopIteration
        try:
            created_university_name: object = next(
                cls._test_data_iterators["university"]["name"]  # noqa: COM812
            )
        except StopIteration as test_data_iterator_error:
            raise NotEnoughTestDataError(
                model_name="university",
                field_name="name",
            ) from test_data_iterator_error

        if not isinstance(created_university_name, str):
            INVALID_TEST_DATA_TYPE_MESSAGE: Final[str] = (
                "created_university_name must be a string."
            )
            raise TypeError(INVALID_TEST_DATA_TYPE_MESSAGE)

        return created_university_name

    @classmethod
    def create_university_short_name(cls) -> str:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a university short name "
                "because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        test_data_iterator_error: StopIteration
        try:
            created_university_short_name: object = next(
                cls._test_data_iterators["university"]["short_name"]  # noqa: COM812
            )
        except StopIteration as test_data_iterator_error:
            raise NotEnoughTestDataError(
                model_name="university",
                field_name="short_name",
            ) from test_data_iterator_error

        if not isinstance(created_university_short_name, str):
            INVALID_TEST_DATA_TYPE_MESSAGE: Final[str] = (
                "created_university_short_name must be a string."
            )
            raise TypeError(INVALID_TEST_DATA_TYPE_MESSAGE)

        return created_university_short_name

    @classmethod
    def create_university_email_domain(cls) -> str:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a university email domain "
                "because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        test_data_iterator_error: StopIteration
        try:
            created_university_email_domain: object = next(
                cls._test_data_iterators["university"]["email_domain"]  # noqa: COM812
            )
        except StopIteration as test_data_iterator_error:
            raise NotEnoughTestDataError(
                model_name="university",
                field_name="email_domain",
            ) from test_data_iterator_error

        if not isinstance(created_university_email_domain, str):
            INVALID_TEST_DATA_TYPE_MESSAGE: Final[str] = (
                "created_university_email_domain must be a string."
            )
            raise TypeError(INVALID_TEST_DATA_TYPE_MESSAGE)

        return created_university_email_domain

    @classmethod
    def create_university(cls, *, save: bool = True) -> University:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a University because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        previous_test_data_iterators: _TestDataWrapper = cls._test_data_iterators.copy()

        try:
            if save:
                return University.objects.create(
                    name=cls.create_university_name(),
                    short_name=cls.create_university_short_name(),
                    email_domain=cls.create_university_email_domain(),
                    founding_date=timezone.now().date(),
                )

            return University(
                name=cls.create_university_name(),
                short_name=cls.create_university_short_name(),
                email_domain=cls.create_university_email_domain(),
                founding_date=timezone.now().date(),
            )

        except (ValidationError, IntegrityError):
            cls._test_data_iterators = previous_test_data_iterators
            raise

    @classmethod
    def create_course_name(cls) -> str:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a course name because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        test_data_iterator_error: StopIteration
        try:
            created_course_name: object = next(
                cls._test_data_iterators["course"]["name"]  # noqa: COM812
            )
        except StopIteration as test_data_iterator_error:
            raise NotEnoughTestDataError(
                model_name="course",
                field_name="name",
            ) from test_data_iterator_error

        if not isinstance(created_course_name, str):
            INVALID_TEST_DATA_TYPE_MESSAGE: Final[str] = (
                "created_course_name must be a string."
            )
            raise TypeError(INVALID_TEST_DATA_TYPE_MESSAGE)

        return created_course_name

    @classmethod
    def create_course_student_type(cls) -> str:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a course student type "
                "because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        test_data_iterator_error: StopIteration
        try:
            created_course_student_type: object = next(
                cls._test_data_iterators["course"]["student_type"]  # noqa: COM812
            )
        except StopIteration as test_data_iterator_error:
            raise NotEnoughTestDataError(
                model_name="course",
                field_name="student_type",
            ) from test_data_iterator_error

        if not isinstance(created_course_student_type, str):
            INVALID_TEST_DATA_TYPE_MESSAGE: Final[str] = (
                "created_course_student_type must be a string."
            )
            raise TypeError(INVALID_TEST_DATA_TYPE_MESSAGE)

        return created_course_student_type

    @classmethod
    def create_course(cls, *, save: bool = True) -> Course:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a Course because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        previous_test_data_iterators: _TestDataWrapper = cls._test_data_iterators.copy()

        try:
            if save:
                return Course.objects.create(
                    name=cls.create_course_name(),
                    student_type=cls.create_course_student_type(),
                    university=cls.create_university(save=True),
                )

            return Course(
                name=cls.create_course_name(),
                student_type=cls.create_course_student_type(),
                university=cls.create_university(save=True),
            )

        except (ValidationError, IntegrityError):
            cls._test_data_iterators = previous_test_data_iterators
            raise

    @classmethod
    def create_module_name(cls) -> str:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a module name because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        test_data_iterator_error: StopIteration
        try:
            created_module_name: object = next(
                cls._test_data_iterators["module"]["name"]  # noqa: COM812
            )
        except StopIteration as test_data_iterator_error:
            raise NotEnoughTestDataError(
                model_name="module",
                field_name="name",
            ) from test_data_iterator_error

        if not isinstance(created_module_name, str):
            INVALID_TEST_DATA_TYPE_MESSAGE: Final[str] = (
                "created_module_name must be a string."
            )
            raise TypeError(INVALID_TEST_DATA_TYPE_MESSAGE)

        return created_module_name

    @classmethod
    def create_module_code(cls) -> str:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a module code because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        test_data_iterator_error: StopIteration
        try:
            created_module_code: object = next(
                cls._test_data_iterators["module"]["code"]  # noqa: COM812
            )
        except StopIteration as test_data_iterator_error:
            raise NotEnoughTestDataError(
                model_name="module",
                field_name="code",
            ) from test_data_iterator_error

        if not isinstance(created_module_code, str):
            INVALID_TEST_DATA_TYPE_MESSAGE: Final[str] = (
                "created_module_code must be a string."
            )
            raise TypeError(INVALID_TEST_DATA_TYPE_MESSAGE)

        return created_module_code

    @classmethod
    def create_module(cls, *, save: bool = True) -> Module:
        if not hasattr(cls, "_test_data_iterators"):
            NO_TEST_DATA_ERROR_MESSAGE: Final[str] = (
                "Cannot create a Module because the test data has not been loaded. "
                "Call the \"set_up()\" class-method to load the test data."
            )
            raise RuntimeError(NO_TEST_DATA_ERROR_MESSAGE)

        previous_test_data_iterators: _TestDataWrapper = cls._test_data_iterators.copy()

        try:
            created_module: Module = (
                Module.objects.create(
                    name=cls.create_module_name(),
                    code=cls.create_module_code(),
                    year_started=timezone.now().date(),
                )
                if save
                else Module(
                    name=cls.create_module_name(),
                    code=cls.create_module_code(),
                    year_started=timezone.now().date(),
                )
            )

        except (ValidationError, IntegrityError):
            cls._test_data_iterators = previous_test_data_iterators
            raise

        return created_module

    @classmethod
    def set_up(cls) -> None:
        cls._test_data_iterators = _TestDataWrapper()


class TestCase(DjangoTestCase):
    @override
    def setUp(self) -> None:
        TestDataGenerator.set_up()

    @staticmethod
    def _sub_test_wrapper(func: _SubTestWrapperFuncCallable) -> _SubTestCallable:
        class _SubTestContextManager(GeneratorContextManager[None]):
            def __enter__(self) -> None:
                self._sid = transaction.savepoint()
                TestDataGenerator.set_up()
                super().__enter__()

            def __exit__(self, typ: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None) -> bool | None:  # noqa: E501
                transaction.savepoint_rollback(self._sid)
                return super().__exit__(typ, value, traceback)

        # noinspection SpellCheckingInspection
        @functools.wraps(func)
        def helper(*args: object, **kwds: object) -> _SubTestContextManager:
            return _SubTestContextManager(func, args, kwds)

        return helper

    subTest: _SubTestCallable = _sub_test_wrapper(  # noqa: N815
        DjangoTestCase.subTest.__wrapped__,  # type: ignore[attr-defined]
    )
