"""Test suite for model signals."""

from collections.abc import Sequence

__all__: Sequence[str] = ()

import re

from django.db import IntegrityError, transaction

from ratemymodule.models import Course, Module, University, User
from ratemymodule.tests.utils import TestCase, TestDataGenerator


class CourseRemovedFromUserSignalTests(TestCase):
    def test_success_user_enrolled_course_set_removed_to_not_empty(self) -> None:
        course1: Course = TestDataGenerator.create_course()
        course2: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=course1.university,
        )

        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                user: User = User.objects.create_user(
                    email=(
                        f"{TestDataGenerator.create_user_email().rpartition("@")[0]}@"
                        f"{course1.university.email_domain}"
                    ),
                    is_staff=user_is_staff,
                )

                user.enrolled_course_set.add(course1)
                user.enrolled_course_set.add(course2)

                with transaction.atomic():
                    integrity_error: IntegrityError
                    try:
                        user.enrolled_course_set.remove(course2)
                    except IntegrityError as integrity_error:
                        SIGNAL_FAILED: bool = bool(
                            re.match(
                                (
                                    r"NOTNULL constraint failed.*"
                                    r"user_enrolled_course_set.*empty"
                                ),
                                integrity_error.args[0],
                            )  # noqa: COM812
                        )
                        if SIGNAL_FAILED:
                            self.fail(
                                f"{type(integrity_error).__name__} raised: "
                                f"{integrity_error.args[0]}"  # noqa: COM812
                            )

                        else:
                            raise integrity_error from integrity_error

                self.assertNotIn(course2, user.enrolled_course_set.all())

    def test_non_staff_user_enrolled_course_set_cleared(self) -> None:
        user: User = User.objects.create_user(
            email=TestDataGenerator.create_user_email(),
            is_staff=False,
        )
        user_university: University | None = user.university
        if not user_university:
            raise RuntimeError

        course: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=user_university,
        )

        user.enrolled_course_set.add(course)

        with transaction.atomic(), self.assertRaisesRegex(IntegrityError, r"NOTNULL constraint failed.*user_enrolled_course_set.*empty"):  # noqa: E501
            user.enrolled_course_set.clear()

        self.assertTrue(user.enrolled_course_set.exists())
        self.assertIn(course, user.enrolled_course_set.all())

    def test_non_staff_user_enrolled_course_set_removed_to_empty(self) -> None:
        user: User = User.objects.create_user(
            email=TestDataGenerator.create_user_email(),
            is_staff=False,
        )
        user_university: University | None = user.university
        if not user_university:
            raise RuntimeError

        course: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=user_university,
        )

        user.enrolled_course_set.add(course)

        with transaction.atomic(), self.assertRaisesRegex(IntegrityError, r"NOTNULL constraint failed.*user_enrolled_course_set.*empty"):  # noqa: E501
            user.enrolled_course_set.remove(course)

        self.assertTrue(user.enrolled_course_set.exists())
        self.assertIn(course, user.enrolled_course_set.all())

    def test_staff_user_enrolled_course_set_cleared(self) -> None:
        user: User = User.objects.create_user(
            email=TestDataGenerator.create_user_email(),
            is_staff=True,
        )
        user_university: University | None = user.university
        if not user_university:
            raise RuntimeError

        course: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=user_university,
        )

        user.enrolled_course_set.add(course)

        with transaction.atomic():
            integrity_error: IntegrityError
            try:
                user.enrolled_course_set.clear()
            except IntegrityError as integrity_error:
                SIGNAL_FAILED: bool = bool(
                    re.match(
                        r"NOTNULL constraint failed.*user_enrolled_course_set.*empty",
                        integrity_error.args[0],
                    )  # noqa: COM812
                )
                if SIGNAL_FAILED:
                    self.fail(
                        f"{type(integrity_error).__name__} raised: {integrity_error.args[0]}"  # noqa: COM812
                    )

                else:
                    raise integrity_error from integrity_error

        self.assertFalse(user.enrolled_course_set.exists())
        self.assertNotIn(course, user.enrolled_course_set.all())

    def test_staff_user_enrolled_course_set_removed_to_empty(self) -> None:
        user: User = User.objects.create_user(
            email=TestDataGenerator.create_user_email(),
            is_staff=True,
        )
        user_university: University | None = user.university
        if not user_university:
            raise RuntimeError

        course: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=user_university,
        )

        user.enrolled_course_set.add(course)

        with transaction.atomic():
            integrity_error: IntegrityError
            try:
                user.enrolled_course_set.remove(course)
            except IntegrityError as integrity_error:
                SIGNAL_FAILED: bool = bool(
                    re.match(
                        r"NOTNULL constraint failed.*user_enrolled_course_set.*empty",
                        integrity_error.args[0],
                    )  # noqa: COM812
                )
                if SIGNAL_FAILED:
                    self.fail(
                        f"{type(integrity_error).__name__} raised: {integrity_error.args[0]}"  # noqa: COM812
                    )

                else:
                    raise integrity_error from integrity_error

        self.assertFalse(user.enrolled_course_set.exists())
        self.assertNotIn(course, user.enrolled_course_set.all())


class UserRemovedFromCourseSignalTests(TestCase):
    def test_success_course_enrolled_user_set_cleared_with_other_courses(self) -> None:
        course1: Course = TestDataGenerator.create_course()
        course2: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=course1.university,
        )

        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                user: User = User.objects.create_user(
                    email=(
                        f"{TestDataGenerator.create_user_email().rpartition("@")[0]}@"
                        f"{course1.university.email_domain}"
                    ),
                    is_staff=user_is_staff,
                )

                course1.enrolled_user_set.add(user)
                course2.enrolled_user_set.add(user)

                with transaction.atomic():
                    integrity_error: IntegrityError
                    try:
                        course2.enrolled_user_set.clear()
                    except IntegrityError as integrity_error:
                        SIGNAL_FAILED: bool = bool(
                            re.match(
                                r"NOTNULL constraint failed.*user_enrolled_course_set.*empty",
                                integrity_error.args[0],
                            )  # noqa: COM812
                        )
                        if SIGNAL_FAILED:
                            self.fail(
                                f"{type(integrity_error).__name__} raised: "
                                f"{integrity_error.args[0]}"  # noqa: COM812
                            )

                        else:
                            raise integrity_error from integrity_error

                self.assertFalse(course2.enrolled_user_set.exists())
                self.assertNotIn(user, course2.enrolled_user_set.all())

    def test_success_course_enrolled_user_removed_with_other_courses(self) -> None:
        course1: Course = TestDataGenerator.create_course()
        course2: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=course1.university,
        )

        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                user: User = User.objects.create_user(
                    email=(
                        f"{TestDataGenerator.create_user_email().rpartition("@")[0]}@"
                        f"{course1.university.email_domain}"
                    ),
                    is_staff=user_is_staff,
                )

                course1.enrolled_user_set.add(user)
                course2.enrolled_user_set.add(user)

                with transaction.atomic():
                    integrity_error: IntegrityError
                    try:
                        course2.enrolled_user_set.remove(user)
                    except IntegrityError as integrity_error:
                        SIGNAL_FAILED: bool = bool(
                            re.match(
                                (
                                    r"NOTNULL constraint failed.*"
                                    r"user_enrolled_course_set.*empty"
                                ),
                                integrity_error.args[0],
                            )  # noqa: COM812
                        )
                        if SIGNAL_FAILED:
                            self.fail(
                                f"{type(integrity_error).__name__} raised: "
                                f"{integrity_error.args[0]}"  # noqa: COM812
                            )

                        else:
                            raise integrity_error from integrity_error

                self.assertFalse(course2.enrolled_user_set.exists())
                self.assertNotIn(user, course2.enrolled_user_set.all())

    def test_course_non_staff_enrolled_user_set_cleared_with_no_other_courses(self) -> None:
        course: Course = TestDataGenerator.create_course()

        user: User = User.objects.create_user(
            email=(
                f"{TestDataGenerator.create_user_email().rpartition("@")[0]}@"
                f"{course.university.email_domain}"
            ),
            is_staff=False,
        )

        course.enrolled_user_set.add(user)

        with transaction.atomic(), self.assertRaisesRegex(IntegrityError, "NOTNULL constraint failed.*user_enrolled_course_set.*empty"):  # noqa: E501
            course.enrolled_user_set.clear()

        self.assertTrue(course.enrolled_user_set.exists())
        self.assertIn(user, course.enrolled_user_set.all())

    def test_course_non_staff_enrolled_user_removed_with_no_other_courses(self) -> None:
        course: Course = TestDataGenerator.create_course()

        user: User = User.objects.create_user(
            email=(
                f"{TestDataGenerator.create_user_email().rpartition("@")[0]}@"
                f"{course.university.email_domain}"
            ),
            is_staff=False,
        )

        course.enrolled_user_set.add(user)

        with transaction.atomic(), self.assertRaisesRegex(IntegrityError, "NOTNULL constraint failed.*user_enrolled_course_set.*empty"):  # noqa: E501
            course.enrolled_user_set.remove(user)

        self.assertTrue(course.enrolled_user_set.exists())
        self.assertIn(user, course.enrolled_user_set.all())

    def test_course_staff_enrolled_user_set_cleared_with_no_other_courses(self) -> None:
        course: Course = TestDataGenerator.create_course()

        user: User = User.objects.create_user(
            email=(
                f"{TestDataGenerator.create_user_email().rpartition("@")[0]}@"
                f"{course.university.email_domain}"
            ),
            is_staff=True,
        )

        course.enrolled_user_set.add(user)

        with transaction.atomic():
            integrity_error: IntegrityError
            try:
                course.enrolled_user_set.clear()
            except IntegrityError as integrity_error:
                SIGNAL_FAILED: bool = bool(
                    re.match(
                        r"NOTNULL constraint failed.*user_enrolled_course_set.*empty",
                        integrity_error.args[0],
                    )  # noqa: COM812
                )
                if SIGNAL_FAILED:
                    self.fail(
                        f"{type(integrity_error).__name__} raised: {integrity_error.args[0]}"  # noqa: COM812
                    )

                else:
                    raise integrity_error from integrity_error

        self.assertFalse(course.enrolled_user_set.exists())
        self.assertNotIn(user, course.enrolled_user_set.all())

    def test_course_staff_enrolled_user_removed_with_no_other_courses(self) -> None:
        course: Course = TestDataGenerator.create_course()

        user: User = User.objects.create_user(
            email=(
                f"{TestDataGenerator.create_user_email().rpartition("@")[0]}@"
                f"{course.university.email_domain}"
            ),
            is_staff=True,
        )

        course.enrolled_user_set.add(user)

        with transaction.atomic():
            integrity_error: IntegrityError
            try:
                course.enrolled_user_set.remove(user)
            except IntegrityError as integrity_error:
                SIGNAL_FAILED: bool = bool(
                    re.match(
                        r"NOTNULL constraint failed.*user_enrolled_course_set.*empty",
                        integrity_error.args[0],
                    )  # noqa: COM812
                )
                if SIGNAL_FAILED:
                    self.fail(
                        f"{type(integrity_error).__name__} raised: {integrity_error.args[0]}"  # noqa: COM812
                    )

                else:
                    raise integrity_error from integrity_error

        self.assertFalse(course.enrolled_user_set.exists())
        self.assertNotIn(user, course.enrolled_user_set.all())


class CourseRemovedFromModuleSignalTests(TestCase):
    def test_success_module_course_set_removed_to_not_empty(self) -> None:
        module: Module = TestDataGenerator.create_module()

        course1: Course = TestDataGenerator.create_course()
        course2: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=course1.university,
        )

        module.course_set.add(course1)
        module.course_set.add(course2)

        with transaction.atomic():
            integrity_error: IntegrityError
            try:
                module.course_set.remove(course2)
            except IntegrityError as integrity_error:
                SIGNAL_FAILED: bool = bool(
                    re.match(
                        r"NOTNULL constraint failed.*module_course_set.*empty",
                        integrity_error.args[0],
                    )  # noqa: COM812
                )
                if SIGNAL_FAILED:
                    self.fail(
                        f"{type(integrity_error).__name__} raised: "
                        f"{integrity_error.args[0]}"  # noqa: COM812
                    )

                else:
                    raise integrity_error from integrity_error

        self.assertNotIn(course2, module.course_set.all())

    def test_module_course_set_cleared(self) -> None:
        module: Module = TestDataGenerator.create_module()

        course: Course = TestDataGenerator.create_course()

        module.course_set.add(course)

        with transaction.atomic(), self.assertRaisesRegex(IntegrityError, r"NOTNULL constraint failed.*module_course_set.*empty"):  # noqa: E501
            module.course_set.clear()

        self.assertTrue(module.course_set.exists())
        self.assertIn(course, module.course_set.all())

    def test_module_course_set_removed_to_empty(self) -> None:
        module: Module = TestDataGenerator.create_module()

        course: Course = TestDataGenerator.create_course()

        module.course_set.add(course)

        with transaction.atomic(), self.assertRaisesRegex(IntegrityError, r"NOTNULL constraint failed.*module_course_set.*empty"):  # noqa: E501
            module.course_set.remove(course)

        self.assertTrue(module.course_set.exists())
        self.assertIn(course, module.course_set.all())


class ModuleRemovedFromCourseSignalTests(TestCase):
    def test_success_course_module_set_cleared_with_other_courses(self) -> None:
        course1: Course = TestDataGenerator.create_course()
        course2: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=course1.university,
        )

        module: Module = TestDataGenerator.create_module()

        course1.module_set.add(module)
        course2.module_set.add(module)

        with transaction.atomic():
            integrity_error: IntegrityError
            try:
                course2.module_set.clear()
            except IntegrityError as integrity_error:
                SIGNAL_FAILED: bool = bool(
                    re.match(
                        r"NOTNULL constraint failed.*module_course_set.*empty",
                        integrity_error.args[0],
                    )  # noqa: COM812
                )
                if SIGNAL_FAILED:
                    self.fail(
                        f"{type(integrity_error).__name__} raised: "
                        f"{integrity_error.args[0]}"  # noqa: COM812
                    )

                else:
                    raise integrity_error from integrity_error

        self.assertFalse(course2.module_set.exists())
        self.assertNotIn(module, course2.module_set.all())

    def test_success_course_module_removed_with_other_courses(self) -> None:
        course1: Course = TestDataGenerator.create_course()
        course2: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=course1.university,
        )

        module: Module = TestDataGenerator.create_module()

        course1.module_set.add(module)
        course2.module_set.add(module)

        with transaction.atomic():
            integrity_error: IntegrityError
            try:
                course2.module_set.remove(module)
            except IntegrityError as integrity_error:
                SIGNAL_FAILED: bool = bool(
                    re.match(
                        r"NOTNULL constraint failed.*module_course_set.*empty",
                        integrity_error.args[0],
                    )  # noqa: COM812
                )
                if SIGNAL_FAILED:
                    self.fail(
                        f"{type(integrity_error).__name__} raised: "
                        f"{integrity_error.args[0]}"  # noqa: COM812
                    )

                else:
                    raise integrity_error from integrity_error

        self.assertFalse(course2.module_set.exists())
        self.assertNotIn(module, course2.module_set.all())

    def test_course_module_set_cleared_with_no_other_courses(self) -> None:
        course: Course = TestDataGenerator.create_course()

        module: Module = TestDataGenerator.create_module()

        course.module_set.add(module)

        with transaction.atomic(), self.assertRaisesRegex(IntegrityError, "NOTNULL constraint failed.*module_course_set.*empty"):  # noqa: E501
            course.module_set.clear()

        self.assertTrue(course.module_set.exists())
        self.assertIn(module, course.module_set.all())

    def test_course_module_removed_with_no_other_courses(self) -> None:
        course: Course = TestDataGenerator.create_course()

        module: Module = TestDataGenerator.create_module()

        course.module_set.add(module)

        with transaction.atomic(), self.assertRaisesRegex(IntegrityError, "NOTNULL constraint failed.*module_course_set.*empty"):  # noqa: E501
            course.module_set.remove(module)

        self.assertTrue(course.module_set.exists())
        self.assertIn(module, course.module_set.all())


class CourseAddedToUserSignalTests(TestCase):
    def test_success_course_at_same_university_added_to_user_with_no_courses(self) -> None:
        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                user: User = User.objects.create_user(
                    email=TestDataGenerator.create_user_email(),
                    is_staff=user_is_staff,
                )
                user_university: University | None = user.university
                if not user_university:
                    raise RuntimeError

                course: Course = Course.objects.create(
                    name=TestDataGenerator.create_course_name(),
                    student_type=TestDataGenerator.create_course_student_type(),
                    university=user_university,
                )

                ENROLLED_COURSE_SET_HAS_CORRECT_STATE: bool = (
                    course not in user.enrolled_course_set.all()
                    and not user.enrolled_course_set.exists()
                    and course.university == user_university
                )
                if not ENROLLED_COURSE_SET_HAS_CORRECT_STATE:
                    raise RuntimeError

                with transaction.atomic():
                    integrity_error: IntegrityError
                    try:
                        user.enrolled_course_set.add(course)
                    except IntegrityError as integrity_error:
                        SIGNAL_FAILED: bool = bool(
                            re.match(
                                (
                                    r"VALIDATION constraint failed.*"
                                    r"user.*cannot be enrolled.*multiple universities"
                                ),
                                integrity_error.args[0],
                            )  # noqa: COM812
                        )
                        if SIGNAL_FAILED:
                            self.fail(
                                f"{type(integrity_error).__name__} raised: "
                                f"{integrity_error.args[0]}"  # noqa: COM812
                            )

                        else:
                            raise integrity_error from integrity_error

                self.assertTrue(user.enrolled_course_set.exists())
                self.assertIn(course, user.enrolled_course_set.all())

    def test_success_course_at_same_university_added_to_user_with_courses(self) -> None:
        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                user: User = User.objects.create_user(
                    email=TestDataGenerator.create_user_email(),
                    is_staff=user_is_staff,
                )
                user_university: University | None = user.university
                if not user_university:
                    raise RuntimeError
                course1: Course = Course.objects.create(
                    name=TestDataGenerator.create_course_name(),
                    student_type=TestDataGenerator.create_course_student_type(),
                    university=user_university,
                )
                user.enrolled_course_set.add(course1)

                course2: Course = Course.objects.create(
                    name=TestDataGenerator.create_course_name(),
                    student_type=TestDataGenerator.create_course_student_type(),
                    university=user_university,
                )

                ENROLLED_COURSE_SET_HAS_CORRECT_STATE: bool = (
                    course1 in user.enrolled_course_set.all()
                    and course2 not in user.enrolled_course_set.all()
                    and user.enrolled_course_set.exists()
                    and course1.university == user_university
                    and course2.university == user_university
                )
                if not ENROLLED_COURSE_SET_HAS_CORRECT_STATE:
                    raise RuntimeError

                with transaction.atomic():
                    integrity_error: IntegrityError
                    try:
                        user.enrolled_course_set.add(course2)
                    except IntegrityError as integrity_error:
                        SIGNAL_FAILED: bool = bool(
                            re.match(
                                (
                                    r"VALIDATION constraint failed.*"
                                    r"user.*cannot be enrolled.*multiple universities"
                                ),
                                integrity_error.args[0],
                            )  # noqa: COM812
                        )
                        if SIGNAL_FAILED:
                            self.fail(
                                f"{type(integrity_error).__name__} raised: "
                                f"{integrity_error.args[0]}"  # noqa: COM812
                            )

                        else:
                            raise integrity_error from integrity_error

                self.assertTrue(user.enrolled_course_set.exists())
                self.assertIn(course2, user.enrolled_course_set.all())

    def test_course_at_different_university_added_to_user_with_no_courses(self) -> None:
        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                user: User = User.objects.create_user(
                    email=TestDataGenerator.create_user_email(with_new_university=True),
                    is_staff=user_is_staff,
                )
                user_university: University | None = user.university
                if not user_university:
                    raise RuntimeError

                course: Course = TestDataGenerator.create_course()

                ENROLLED_COURSE_SET_HAS_CORRECT_STATE: bool = (
                    course not in user.enrolled_course_set.all()
                    and not user.enrolled_course_set.exists()
                    and course.university != user_university
                )
                if not ENROLLED_COURSE_SET_HAS_CORRECT_STATE:
                    raise RuntimeError

                with transaction.atomic(), self.assertRaisesRegex(IntegrityError, r"VALIDATION constraint failed.*user.*cannot be enrolled.*multiple universities"):  # noqa: E501
                    user.enrolled_course_set.add(course)

                self.assertFalse(user.enrolled_course_set.exists())
                self.assertNotIn(course, user.enrolled_course_set.all())

    def test_course_at_different_university_added_to_user_with_courses(self) -> None:
        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                user: User = User.objects.create_user(
                    email=TestDataGenerator.create_user_email(with_new_university=True),
                    is_staff=user_is_staff,
                )
                user_university: University | None = user.university
                if not user_university:
                    raise RuntimeError
                course1: Course = Course.objects.create(
                    name=TestDataGenerator.create_course_name(),
                    student_type=TestDataGenerator.create_course_student_type(),
                    university=user_university,
                )
                user.enrolled_course_set.add(course1)

                course2: Course = TestDataGenerator.create_course()

                ENROLLED_COURSE_SET_HAS_CORRECT_STATE: bool = (
                    course1 in user.enrolled_course_set.all()
                    and course2 not in user.enrolled_course_set.all()
                    and user.enrolled_course_set.exists()
                    and course1.university == user_university
                    and course2.university != user_university
                    and course2.university != course1.university
                )
                if not ENROLLED_COURSE_SET_HAS_CORRECT_STATE:
                    raise RuntimeError

                with transaction.atomic(), self.assertRaisesRegex(IntegrityError, r"VALIDATION constraint failed.*user.*cannot be enrolled.*multiple universities"):  # noqa: E501
                    user.enrolled_course_set.add(course2)

                self.assertNotIn(course2, user.enrolled_course_set.all())


class UserAddedToCourseSignalTests(TestCase):
    def test_success_user_with_no_courses_added_to_course_at_same_university(self) -> None:
        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                user: User = User.objects.create_user(
                    email=TestDataGenerator.create_user_email(),
                    is_staff=user_is_staff,
                )
                user_university: University | None = user.university
                if not user_university:
                    raise RuntimeError

                course: Course = Course.objects.create(
                    name=TestDataGenerator.create_course_name(),
                    student_type=TestDataGenerator.create_course_student_type(),
                    university=user_university,
                )

                ENROLLED_COURSE_SET_HAS_CORRECT_STATE: bool = (
                    user not in course.enrolled_user_set.all()
                    and not user.enrolled_course_set.exists()
                    and bool(user.university)
                    and user.university == course.university
                )
                if not ENROLLED_COURSE_SET_HAS_CORRECT_STATE:
                    raise RuntimeError

                with transaction.atomic():
                    integrity_error: IntegrityError
                    try:
                        course.enrolled_user_set.add(user)
                    except IntegrityError as integrity_error:
                        SIGNAL_FAILED: bool = bool(
                            re.match(
                                (
                                    r"VALIDATION constraint failed.*"
                                    r"user.*cannot be enrolled.*multiple universities"
                                ),
                                integrity_error.args[0],
                            )  # noqa: COM812
                        )
                        if SIGNAL_FAILED:
                            self.fail(
                                f"{type(integrity_error).__name__} raised: "
                                f"{integrity_error.args[0]}"  # noqa: COM812
                            )

                        else:
                            raise integrity_error from integrity_error

                self.assertTrue(course.enrolled_user_set.exists())
                self.assertIn(user, course.enrolled_user_set.all())

    def test_success_user_with_courses_added_to_course_at_same_university(self) -> None:
        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                user: User = User.objects.create_user(
                    email=TestDataGenerator.create_user_email(),
                    is_staff=user_is_staff,
                )
                user_university: University | None = user.university
                if not user_university:
                    raise RuntimeError
                course1: Course = Course.objects.create(
                    name=TestDataGenerator.create_course_name(),
                    student_type=TestDataGenerator.create_course_student_type(),
                    university=user_university,
                )
                user.enrolled_course_set.add(course1)

                course2: Course = Course.objects.create(
                    name=TestDataGenerator.create_course_name(),
                    student_type=TestDataGenerator.create_course_student_type(),
                    university=user_university,
                )

                ENROLLED_COURSE_SET_HAS_CORRECT_STATE: bool = (
                    course1 in user.enrolled_course_set.all()
                    and user not in course2.enrolled_user_set.all()
                    and user.enrolled_course_set.exists()
                    and bool(user.university)
                    and user.university == course1.university
                    and user.university == course2.university
                )
                if not ENROLLED_COURSE_SET_HAS_CORRECT_STATE:
                    raise RuntimeError

                with transaction.atomic():
                    integrity_error: IntegrityError
                    try:
                        course2.enrolled_user_set.add(user)
                    except IntegrityError as integrity_error:
                        SIGNAL_FAILED: bool = bool(
                            re.match(
                                (
                                    r"VALIDATION constraint failed.*"
                                    r"user.*cannot be enrolled.*multiple universities"
                                ),
                                integrity_error.args[0],
                            )  # noqa: COM812
                        )
                        if SIGNAL_FAILED:
                            self.fail(
                                f"{type(integrity_error).__name__} raised: "
                                f"{integrity_error.args[0]}"  # noqa: COM812
                            )

                        else:
                            raise integrity_error from integrity_error

                self.assertTrue(course2.enrolled_user_set.exists())
                self.assertIn(user, course2.enrolled_user_set.all())

    def test_user_with_no_courses_added_to_course_at_different_university(self) -> None:
        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                course: Course = TestDataGenerator.create_course()

                user: User = User.objects.create_user(
                    email=TestDataGenerator.create_user_email(with_new_university=True),
                    is_staff=user_is_staff,
                )

                ENROLLED_COURSE_SET_HAS_CORRECT_STATE: bool = (
                    user not in course.enrolled_user_set.all()
                    and not user.enrolled_course_set.exists()
                    and bool(user.university)
                    and user.university != course.university
                )
                if not ENROLLED_COURSE_SET_HAS_CORRECT_STATE:
                    raise RuntimeError

                with transaction.atomic(), self.assertRaisesRegex(IntegrityError, r"VALIDATION constraint failed.*user.*cannot be enrolled.*multiple universities"):  # noqa: E501
                    course.enrolled_user_set.add(user)

                self.assertNotIn(user, course.enrolled_user_set.all())

    def test_user_with_courses_added_to_course_at_different_university(self) -> None:
        user_is_staff: bool
        for user_is_staff in (True, False):
            with self.subTest(user_is_staff=user_is_staff):
                user: User = User.objects.create_user(
                    email=TestDataGenerator.create_user_email(with_new_university=True),
                    is_staff=user_is_staff,
                )
                user_university: University | None = user.university
                if not user_university:
                    raise RuntimeError
                course1: Course = Course.objects.create(
                    name=TestDataGenerator.create_course_name(),
                    student_type=TestDataGenerator.create_course_student_type(),
                    university=user_university,
                )
                user.enrolled_course_set.add(course1)

                course2: Course = TestDataGenerator.create_course()

                ENROLLED_COURSE_SET_HAS_CORRECT_STATE: bool = (
                    course1 in user.enrolled_course_set.all()
                    and user not in course2.enrolled_user_set.all()
                    and user.enrolled_course_set.exists()
                    and course1.university == user_university
                    and bool(user.university)
                    and user.university != course2.university
                    and course2.university != course1.university
                )
                if not ENROLLED_COURSE_SET_HAS_CORRECT_STATE:
                    raise RuntimeError

                with transaction.atomic(), self.assertRaisesRegex(IntegrityError, r"VALIDATION constraint failed.*user.*cannot be enrolled.*multiple universities"):  # noqa: E501
                    course2.enrolled_user_set.add(user)

                self.assertNotIn(user, course2.enrolled_user_set.all())


class CourseAddedToModuleSignalTests(TestCase):
    def test_success_course_added_to_module_with_no_courses(self) -> None:
        module: Module = TestDataGenerator.create_module()

        course: Course = TestDataGenerator.create_course()

        COURSE_SET_HAS_CORRECT_STATE: bool = (
            course not in module.course_set.all()
            and not module.course_set.exists()
        )
        if not COURSE_SET_HAS_CORRECT_STATE:
            raise RuntimeError

        with transaction.atomic():
            integrity_error: IntegrityError
            try:
                module.course_set.add(course)
            except IntegrityError as integrity_error:
                SIGNAL_FAILED: bool = bool(
                    re.match(
                        (
                            r"VALIDATION constraint failed.*"
                            r"module.*cannot be attached.*multiple universities"
                        ),
                        integrity_error.args[0],
                    )  # noqa: COM812
                )
                if SIGNAL_FAILED:
                    self.fail(
                        f"{type(integrity_error).__name__} raised: "
                        f"{integrity_error.args[0]}"  # noqa: COM812
                    )

                else:
                    raise integrity_error from integrity_error

        self.assertTrue(module.course_set.exists())
        self.assertIn(course, module.course_set.all())

    def test_success_course_at_same_university_added_to_module_with_courses(self) -> None:
        module: Module = TestDataGenerator.create_module()
        course1: Course = TestDataGenerator.create_course()
        module.course_set.add(course1)

        course2: Course = Course.objects.create(
            name=TestDataGenerator.create_course_name(),
            student_type=TestDataGenerator.create_course_student_type(),
            university=module.university,
        )

        ENROLLED_COURSE_SET_HAS_CORRECT_STATE: bool = (
            course1 in module.course_set.all()
            and module.course_set.exists()
            and course2 not in module.course_set.all()
            and course1.university == module.university
            and course2.university == module.university
        )
        if not ENROLLED_COURSE_SET_HAS_CORRECT_STATE:
            raise RuntimeError

        with transaction.atomic():
            integrity_error: IntegrityError
            try:
                module.course_set.add(course2)
            except IntegrityError as integrity_error:
                SIGNAL_FAILED: bool = bool(
                    re.match(
                        (
                            r"VALIDATION constraint failed.*"
                            r"module.*cannot be attached.*multiple universities"
                        ),
                        integrity_error.args[0],
                    )  # noqa: COM812
                )
                if SIGNAL_FAILED:
                    self.fail(
                        f"{type(integrity_error).__name__} raised: "
                        f"{integrity_error.args[0]}"  # noqa: COM812
                    )

                else:
                    raise integrity_error from integrity_error

        self.assertTrue(module.course_set.exists())
        self.assertIn(course2, module.course_set.all())

    def test_course_at_different_university_added_to_module_with_courses(self) -> None:
        module: Module = TestDataGenerator.create_module()
        course1: Course = TestDataGenerator.create_course()
        module.course_set.add(course1)

        course2: Course = TestDataGenerator.create_course()

        ENROLLED_COURSE_SET_HAS_CORRECT_STATE: bool = (
            course1 in module.course_set.all()
            and course2 not in module.course_set.all()
            and module.course_set.exists()
            and course1.university == module.university
            and course2.university != module.university
            and course2.university != course1.university
        )
        if not ENROLLED_COURSE_SET_HAS_CORRECT_STATE:
            raise RuntimeError

        with transaction.atomic(), self.assertRaisesRegex(IntegrityError, r"VALIDATION constraint failed.*module.*cannot be attached.*multiple universities"):  # noqa: E501
            module.course_set.add(course2)

        self.assertNotIn(course2, module.course_set.all())
