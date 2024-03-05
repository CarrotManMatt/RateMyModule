"""Custom forms to edit the details of models within the admin interface."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "UserCreationForm",
    "UserChangeForm",
    "PostModelForm",
    "CourseModelForm",
    "ModuleModelForm"
)

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Final, override

from django import forms
from django.contrib.admin import widgets as admin_widgets
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.forms import ModelForm as DjangoModelForm
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList
from django.utils.datastructures import MultiValueDict
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import QuerySetAny

from ratemymodule.models import Course, Module, Post, University, User

if TYPE_CHECKING:
    from django.db.models import QuerySet


class _BaseUserCleanForm(forms.ModelForm[User]):
    @staticmethod
    def _ensure_superusers_are_staff(cleaned_data: dict[str, object]) -> dict[str, object]:
        is_staff: object | None = cleaned_data.get("is_staff")
        if is_staff is None:
            return cleaned_data
        if not isinstance(is_staff, bool):
            raise TypeError

        is_superuser: object | None = cleaned_data.get("is_superuser")
        if is_superuser is None:
            return cleaned_data
        if not isinstance(is_superuser, bool):
            raise TypeError

        if is_superuser:
            cleaned_data["is_staff"] = True

        return cleaned_data

    @staticmethod
    def _validate_enrolled_course_set_exists(cleaned_data: dict[str, object]) -> None:
        is_staff: object | None = cleaned_data.get("is_staff")
        if is_staff is None:
            return
        if not isinstance(is_staff, bool):
            raise TypeError

        is_superuser: object | None = cleaned_data.get("is_superuser")
        if is_superuser is None:
            return
        if not isinstance(is_superuser, bool):
            raise TypeError

        enrolled_course_set: object | None = cleaned_data.get("enrolled_course_set")
        if enrolled_course_set is None:
            return
        if not isinstance(enrolled_course_set, QuerySetAny):
            raise TypeError

        # noinspection PyUnresolvedReferences
        if not (is_staff or is_superuser) and not enrolled_course_set.exists():
            raise ValidationError(
                {"enrolled_course_set": _("This field is required.")},
                code="required"
            )

    @staticmethod
    def _validate_no_posts_about_modules_on_removed_courses(cleaned_data: dict[str, object], instance: User) -> None:  # noqa: E501
        if not instance.pk:
            return

        enrolled_course_set: object | None = cleaned_data.get("enrolled_course_set")
        if enrolled_course_set is None:
            return
        if not isinstance(enrolled_course_set, QuerySetAny):
            raise TypeError

        POSTS_ABOUT_MODULES_ON_REMOVED_COURSES: Final[bool] = (
            Post.objects.filter(
                user=instance,
                module__course_set__pk__in=instance.enrolled_course_set.exclude(
                    pk__in=enrolled_course_set
                )
            ).exists()
        )
        if POSTS_ABOUT_MODULES_ON_REMOVED_COURSES:
            raise ValidationError(
                {
                    "enrolled_course_set": _(
                        "Courses cannot be removed from a user if they have made posts "
                        "about modules attached to that course."
                    )
                },
                code="invalid"
            )

    @staticmethod
    def _validate_no_courses_across_multiple_universities(cleaned_data: dict[str, object], instance: User) -> None:  # noqa: E501
        if not instance.pk:
            return

        email: object | None = cleaned_data.get("email")
        if email is None:
            return
        if not isinstance(email, str):
            raise TypeError

        is_staff: object | None = cleaned_data.get("is_staff")
        if is_staff is None:
            return
        if not isinstance(is_staff, bool):
            raise TypeError

        is_superuser: object | None = cleaned_data.get("is_superuser")
        if is_superuser is None:
            return
        if not isinstance(is_superuser, bool):
            raise TypeError

        enrolled_course_set: object | None = cleaned_data.get("enrolled_course_set")
        if enrolled_course_set is None:
            return
        if not isinstance(enrolled_course_set, QuerySetAny):
            raise TypeError

        try:
            # noinspection PyUnresolvedReferences,PyProtectedMember
            COURSES_ACROSS_MULTIPLE_UNIVERSITIES: Final[bool] = (
                enrolled_course_set.exclude(
                    university=instance._get_university_from_email_domain(  # noqa: SLF001
                        email.rpartition("@")[2],
                        is_staff=any((is_staff, is_superuser))
                    )
                ).exists()
            )

        except University.DoesNotExist:
            return

        if COURSES_ACROSS_MULTIPLE_UNIVERSITIES:
            raise ValidationError(
                {
                    "enrolled_course_set": _(
                        "A user cannot be enrolled in courses "
                        "across multiple universities."
                    )
                },
                code="invalid"
            )

    @override
    def clean(self) -> dict[str, object] | None:
        cleaned_data: dict[str, object] | None = super().clean()

        if cleaned_data:
            cleaned_data = self._ensure_superusers_are_staff(cleaned_data)

            self._validate_enrolled_course_set_exists(cleaned_data)
            self._validate_no_posts_about_modules_on_removed_courses(
                cleaned_data,
                self.instance
            )
            self._validate_no_courses_across_multiple_universities(
                cleaned_data,
                self.instance
            )

        return cleaned_data


class UserCreationForm(_BaseUserCleanForm, DjangoUserCreationForm[User]):
    """Custom form to add a new instance of a `User` object within the admin interface."""

    template_name = "admin/change_form.html"


class UserChangeForm(_BaseUserCleanForm, DjangoUserChangeForm[User]):
    """Custom form to edit the details of a `User` object within the admin interface."""


class PostModelForm(DjangoModelForm[Post]):
    """Custom form to edit the details of a `Post` object within the admin interface."""

    liked_user_set = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=admin_widgets.FilteredSelectMultiple(
            verbose_name=_("Liked-By Users"),
            is_stacked=False
        ),
        help_text=_(
            "The set of users that have liked this post. "
            "Hold down “Control”, or “Command” on a Mac, to select more than one."
        )
    )
    disliked_user_set = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=admin_widgets.FilteredSelectMultiple(
            verbose_name=_("Disliked-By Users"),
            is_stacked=False
        ),
        help_text=_(
            "The set of users that have disliked this post. "
            "Hold down “Control”, or “Command” on a Mac, to select more than one."
        )
    )

    @override
    def __init__(self, data: Mapping[str, object] | None = None, files: MultiValueDict[str, UploadedFile] | None = None, auto_id: bool | str = "id_%s", prefix: str | None = None, initial: Mapping[str, object] | None = None, error_class: type[ErrorList] = ErrorList, label_suffix: str | None = None, empty_permitted: bool = False, instance: Post | None = None, use_required_attribute: bool | None = None, renderer: BaseRenderer | None = None) -> None:  # noqa: E501
        super().__init__(
            data=data,
            files=files,
            auto_id=auto_id,
            prefix=prefix,
            initial=initial,
            error_class=error_class,
            label_suffix=label_suffix,
            empty_permitted=empty_permitted,
            instance=instance,
            use_required_attribute=use_required_attribute,
            renderer=renderer
        )

        if self.instance.pk:
            self.fields["liked_user_set"].initial = self.instance.liked_user_set.all()
            self.fields["disliked_user_set"].initial = self.instance.disliked_user_set.all()

    @override
    def save(self, commit: bool = True) -> Post:
        post: Post = super().save(commit=False)

        if commit:
            post.save()

        if post.pk:
            m2m_requires_save: bool = False

            liked_user_set: QuerySet[User] | None = self.cleaned_data.get(
                "liked_user_set",
                None
            )
            if liked_user_set is not None:
                if not isinstance(liked_user_set, QuerySetAny):
                    raise TypeError
                post.liked_user_set.set(liked_user_set)
                m2m_requires_save = True

            disliked_user_set: QuerySet[User] | None = self.cleaned_data.get(
                "disliked_user_set",
                None
            )
            if disliked_user_set is not None:
                if not isinstance(disliked_user_set, QuerySetAny):
                    raise TypeError
                post.disliked_user_set.set(disliked_user_set)
                m2m_requires_save = True

            if m2m_requires_save:
                self.save_m2m()

        return post

    @staticmethod
    def _validate_user_has_taken_module(cleaned_data: dict[str, object], instance: Post) -> None:  # noqa: E501
        if not instance.pk:
            return

        user: object | None = cleaned_data.get("user")
        if user is None:
            return
        if not isinstance(user, User):
            raise TypeError

        # NOTE: This error should only be raised from the form clean if it was the many-to-many connection that changed (not if the user changed)
        if user != instance.user:
            return

        module: object | None = cleaned_data.get("module")
        if module is None:
            return
        if not isinstance(module, Module):
            raise TypeError

        if module not in user.module_set.all():
            raise ValidationError(
                {
                    "module": _(
                        "You cannot create posts about modules that you have not taken."
                    )
                },
                code="invalid"
            )

    @override
    def clean(self) -> dict[str, object] | None:
        cleaned_data: dict[str, object] | None = super().clean()

        if cleaned_data:
            self._validate_user_has_taken_module(cleaned_data, self.instance)

        return cleaned_data


class CourseModelForm(DjangoModelForm[Course]):
    """Custom form to edit the details of a `Course` object within the admin interface."""

    module_set = forms.ModelMultipleChoiceField(
        queryset=Module.objects.all(),
        required=False,
        widget=admin_widgets.FilteredSelectMultiple(
            verbose_name=_("Modules"),
            is_stacked=False
        ),
        help_text=_(
            "The set of modules on this course. "
            "Hold down “Control”, or “Command” on a Mac, to select more than one."
        ),
        label=_("Attached Modules")
    )
    enrolled_user_set = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=admin_widgets.FilteredSelectMultiple(
            verbose_name=_("Enrolled Users"),
            is_stacked=False
        ),
        help_text=_(
            "The set of users enrolled on this course. "
            "Hold down “Control”, or “Command” on a Mac, to select more than one."
        ),
        label=_("Enrolled Users")
    )

    @override
    def __init__(self, data: Mapping[str, object] | None = None, files: MultiValueDict[str, UploadedFile] | None = None, auto_id: bool | str = "id_%s", prefix: str | None = None, initial: Mapping[str, object] | None = None, error_class: type[ErrorList] = ErrorList, label_suffix: str | None = None, empty_permitted: bool = False, instance: Course | None = None, use_required_attribute: bool | None = None, renderer: BaseRenderer | None = None) -> None:  # noqa: E501
        super().__init__(
            data=data,
            files=files,
            auto_id=auto_id,
            prefix=prefix,
            initial=initial,
            error_class=error_class,
            label_suffix=label_suffix,
            empty_permitted=empty_permitted,
            instance=instance,
            use_required_attribute=use_required_attribute,
            renderer=renderer
        )

        if self.instance.pk:
            self.fields["module_set"].initial = self.instance.module_set.all()
            self.fields["enrolled_user_set"].initial = self.instance.enrolled_user_set.all()

    @override
    def save(self, commit: bool = True) -> Course:
        course: Course = super().save(commit=False)

        if commit:
            course.save()

        if course.pk:
            m2m_requires_save: bool = False

            module_set: QuerySet[Module] | None = self.cleaned_data.get(
                "module_set",
                None
            )
            if module_set is not None:
                if not isinstance(module_set, QuerySetAny):
                    raise TypeError
                course.module_set.set(module_set)
                m2m_requires_save = True

            enrolled_user_set: QuerySet[User] | None = self.cleaned_data.get(
                "enrolled_user_set",
                None
            )
            if enrolled_user_set is not None:
                if not isinstance(enrolled_user_set, QuerySetAny):
                    raise TypeError
                course.enrolled_user_set.set(enrolled_user_set)
                m2m_requires_save = True

            if m2m_requires_save:
                self.save_m2m()

        return course

    @staticmethod
    def _validate_no_modules_across_multiple_universities(cleaned_data: dict[str, object]) -> None:  # noqa: E501
        university: object | None = cleaned_data.get("university")
        if university is None:
            return
        if not isinstance(university, University):
            raise TypeError

        module_set: object | None = cleaned_data.get("module_set")
        if module_set is None:
            return
        if not isinstance(module_set, QuerySetAny):
            raise TypeError

        other_university_module: Module
        # noinspection PyUnresolvedReferences
        for other_university_module in module_set.all():
            if other_university_module.university != university:
                raise ValidationError(
                    {
                        "module_set": _(
                            "All modules on this course "
                            "must belong to the same university "
                            "that this course belongs to."
                        )
                    },
                    code="invalid"
                )

    @staticmethod
    def _validate_no_module_on_course_with_same_name_exists(cleaned_data: dict[str, object]) -> None:  # noqa: E501
        module_set: object | None = cleaned_data.get("module_set")
        if module_set is None:
            return
        if not isinstance(module_set, QuerySetAny):
            raise TypeError

        other_university_module: Module
        # noinspection PyUnresolvedReferences
        for other_university_module in module_set.all():
            # noinspection PyUnresolvedReferences
            MODULE_WITH_NAME_ALREADY_EXISTS_ON_COURSE: bool = module_set.exclude(
                pk=other_university_module.pk
            ).filter(
                name=other_university_module.name
            ).exists()

            if MODULE_WITH_NAME_ALREADY_EXISTS_ON_COURSE:
                raise ValidationError(
                    {
                        "module_set": _(
                            "Modules cannot be added to this course "
                            "if they share a name with existing modules "
                            "attached to this course."
                        )
                    },
                    code="invalid"
                )

    @staticmethod
    def _validate_no_module_on_course_with_same_code_exists(cleaned_data: dict[str, object]) -> None:  # noqa: E501
        module_set: object | None = cleaned_data.get("module_set")
        if module_set is None:
            return
        if not isinstance(module_set, QuerySetAny):
            raise TypeError

        other_university_module: Module
        # noinspection PyUnresolvedReferences
        for other_university_module in module_set.all():
            # noinspection PyUnresolvedReferences
            MODULE_WITH_CODE_ALREADY_EXISTS_ON_COURSE: bool = module_set.exclude(
                pk=other_university_module.pk
            ).filter(
                code=other_university_module.code
            ).exists()

            if MODULE_WITH_CODE_ALREADY_EXISTS_ON_COURSE:
                raise ValidationError(
                    {
                        "module_set": _(
                            "Modules cannot be added to this course "
                            "if they share a reference code with existing modules "
                            "attached to this course."
                        )
                    },
                    code="invalid"
                )

    @staticmethod
    def _validate_no_enrolled_users_across_multiple_universities(cleaned_data: dict[str, object]) -> None:  # noqa: E501
        university: object | None = cleaned_data.get("university")
        if university is None:
            return
        if not isinstance(university, University):
            raise TypeError

        enrolled_user_set: object | None = cleaned_data.get("enrolled_user_set")
        if enrolled_user_set is None:
            return
        if not isinstance(enrolled_user_set, QuerySetAny):
            raise TypeError

        other_university_user: User
        # noinspection PyUnresolvedReferences
        for other_university_user in enrolled_user_set.all():
            if other_university_user.university != university:
                raise ValidationError(
                    {
                        "enrolled_user_set": _(
                            "All users enrolled on this course "
                            "must belong to the same university "
                            "that this course belongs to."
                        )
                    },
                    code="invalid"
                )

    @staticmethod
    def _validate_removed_modules_have_no_posts_made_about_them(cleaned_data: dict[str, object], instance: Course) -> None:  # noqa: E501
        if not instance.pk:
            return

        module_set: object | None = cleaned_data.get("module_set")
        if module_set is None:
            return
        if not isinstance(module_set, QuerySetAny):
            raise TypeError

        REMOVED_MODULES_HAVE_POSTS_MADE_ABOUT_THEM_BY_ENROLLED_USERS: Final[bool] = (
            Post.objects.filter(
                module__pk__in=instance.module_set.exclude(pk__in=module_set)
            ).exists()
        )
        if REMOVED_MODULES_HAVE_POSTS_MADE_ABOUT_THEM_BY_ENROLLED_USERS:
            raise ValidationError(
                {
                    "module_set": _(
                        "Modules cannot be removed from this course "
                        "if there are posts made about them, "
                        "by users enrolled on this course."
                    )
                },
                code="invalid"
            )

    @staticmethod
    def _validate_removed_users_have_no_made_posts(cleaned_data: dict[str, object], instance: Course) -> None:  # noqa: E501
        if not instance.pk:
            return

        enrolled_user_set: object | None = cleaned_data.get("enrolled_user_set")
        if enrolled_user_set is None:
            return
        if not isinstance(enrolled_user_set, QuerySetAny):
            raise TypeError

        REMOVED_USERS_HAVE_MADE_POSTS_ABOUT_ATTACHED_MODULES: Final[bool] = (
            Post.objects.filter(
                user__pk__in=instance.enrolled_user_set.exclude(pk__in=enrolled_user_set)
            ).exists()
        )
        if REMOVED_USERS_HAVE_MADE_POSTS_ABOUT_ATTACHED_MODULES:
            raise ValidationError(
                {
                    "enrolled_user_set": _(
                        "Users cannot be removed from this course "
                        "if they have made posts, also attached to this course."
                    )
                },
                code="invalid"
            )

    @staticmethod
    def _validate_removed_modules_have_remaining_courses(cleaned_data: dict[str, object], instance: Course) -> None:  # noqa: E501
        if not instance.pk:
            return

        module_set: object | None = cleaned_data.get("module_set")
        if module_set is None:
            return
        if not isinstance(module_set, QuerySetAny):
            raise TypeError

        no_courses_module: Module
        for no_courses_module in instance.module_set.exclude(pk__in=module_set):
            if not no_courses_module.course_set.exclude(pk=instance.pk).exists():
                raise ValidationError(
                    {
                        "module_set": _(
                            "Modules cannot be removed from this course "
                            "if they are not attached to any other courses."
                        )
                    },
                    code="required"
                )

    @staticmethod
    def _validate_removed_users_have_remaining_enrolled_courses(cleaned_data: dict[str, object], instance: Course) -> None:  # noqa: E501
        if not instance.pk:
            return

        enrolled_user_set: object | None = cleaned_data.get("enrolled_user_set")
        if enrolled_user_set is None:
            return
        if not isinstance(enrolled_user_set, QuerySetAny):
            raise TypeError

        REMOVED_ENROLLED_USERS: Iterable[User] = (
            instance.enrolled_user_set.exclude(pk__in=enrolled_user_set)
        )

        no_enrolled_courses_user: User
        for no_enrolled_courses_user in REMOVED_ENROLLED_USERS:
            USER_WOULD_HAVE_NO_COURSES: bool = (
                not no_enrolled_courses_user.enrolled_course_set.exclude(
                    pk=instance.pk
                ).exists()
            )
            if not no_enrolled_courses_user.is_staff and USER_WOULD_HAVE_NO_COURSES:
                raise ValidationError(
                    {
                        "enrolled_user_set": _(
                            "Users cannot be removed from this course "
                            "if they are not enrolled in any other courses."
                        )
                    },
                    code="required"
                )

    @override
    def clean(self) -> dict[str, object] | None:
        cleaned_data: dict[str, object] | None = super().clean()

        if cleaned_data:
            self._validate_no_modules_across_multiple_universities(cleaned_data)
            self._validate_no_module_on_course_with_same_name_exists(cleaned_data)
            self._validate_no_module_on_course_with_same_code_exists(cleaned_data)
            self._validate_no_enrolled_users_across_multiple_universities(cleaned_data)
            self._validate_removed_modules_have_no_posts_made_about_them(
                cleaned_data,
                self.instance
            )
            self._validate_removed_users_have_no_made_posts(cleaned_data, self.instance)
            self._validate_removed_modules_have_remaining_courses(cleaned_data, self.instance)
            self._validate_removed_users_have_remaining_enrolled_courses(
                cleaned_data,
                self.instance
            )

        return cleaned_data


class ModuleModelForm(DjangoModelForm[Module]):
    """Custom form to edit the details of a `Module` object within the admin interface."""

    @staticmethod
    def _validate_course_set_exists(cleaned_data: dict[str, object]) -> None:
        course_set: object | None = cleaned_data.get("course_set")
        if course_set is None:
            return
        if not isinstance(course_set, QuerySetAny):
            raise TypeError

        # noinspection PyUnresolvedReferences
        if not course_set.exists():
            raise ValidationError(
                {"course_set": _("This field is required.")},
                code="required"
            )

    @staticmethod
    def _validate_all_courses_at_same_university(cleaned_data: dict[str, object]) -> None:
        course_set: object | None = cleaned_data.get("course_set")
        if course_set is None:
            return
        if not isinstance(course_set, QuerySetAny):
            raise TypeError

        # noinspection PyUnresolvedReferences
        if course_set.exclude(university=course_set.all()[0].university).exists():
            raise ValidationError(
                {
                    "course_set": _(
                        "All courses this module is attached to "
                        "must be at the same university."
                    )
                },
                code="invalid"
            )

    @staticmethod
    def _validate_no_posts_from_users_on_removed_courses(cleaned_data: dict[str, object], instance: Module) -> None:  # noqa: E501
        if not instance.pk:
            return

        course_set: object | None = cleaned_data.get("course_set")
        if course_set is None:
            return
        if not isinstance(course_set, QuerySetAny):
            raise TypeError

        MODULE_HAS_POSTS_FROM_USERS_ON_REMOVED_COURSES: Final[bool] = (
            Post.objects.filter(
                module=instance,
                user__enrolled_course_set__pk__in=instance.course_set.exclude(
                    pk__in=course_set
                )
            ).exists()
        )
        if MODULE_HAS_POSTS_FROM_USERS_ON_REMOVED_COURSES:
            raise ValidationError(
                {
                    "course_set": _(
                        "Courses cannot be removed from a module "
                        "if it has posts made about it "
                        "by users enrolled on that course."
                    )
                },
                code="invalid"
            )

    @staticmethod
    def _validate_module_name_is_unique_within_university(cleaned_data: dict[str, object], instance: Module) -> None:  # noqa: E501
        course_set: object | None = cleaned_data.get("course_set")
        if course_set is None:
            return
        if not isinstance(course_set, QuerySetAny):
            raise TypeError

        name: object | None = cleaned_data.get("name")
        if name is None:
            return
        if not isinstance(name, str):
            raise TypeError

        # noinspection PyUnresolvedReferences
        university: University = course_set.all()[0].university

        conflicting_name_module_set: QuerySet[Module] = university.module_set.filter(name=name)

        if instance.pk:
            conflicting_name_module_set = conflicting_name_module_set.exclude(pk=instance.pk)

        if conflicting_name_module_set.exists():
            raise ValidationError(
                _("A module with this name already exists at %(university)s."),
                params={"university": university},
                code="unique"
            )

    @staticmethod
    def _validate_module_code_is_unique_within_university(cleaned_data: dict[str, object], instance: Module) -> None:  # noqa: E501
        course_set: object | None = cleaned_data.get("course_set")
        if course_set is None:
            return
        if not isinstance(course_set, QuerySetAny):
            raise TypeError

        code: object | None = cleaned_data.get("code")
        if code is None:
            return
        if not isinstance(code, str):
            raise TypeError

        # noinspection PyUnresolvedReferences
        university: University = course_set.all()[0].university

        conflicting_code_module_set: QuerySet[Module] = university.module_set.filter(code=code)

        if instance.pk:
            conflicting_code_module_set = conflicting_code_module_set.exclude(pk=instance.pk)

        if conflicting_code_module_set.exists():
            raise ValidationError(
                _("A module with this reference code already exists at %(university)s."),
                params={"university": university},
                code="unique"
            )

    @override
    def clean(self) -> dict[str, object] | None:
        cleaned_data: dict[str, object] | None = super().clean()

        if cleaned_data:
            self._validate_course_set_exists(cleaned_data)
            self._validate_all_courses_at_same_university(cleaned_data)
            self._validate_no_posts_from_users_on_removed_courses(cleaned_data, self.instance)
            self._validate_module_name_is_unique_within_university(cleaned_data, self.instance)
            self._validate_module_code_is_unique_within_university(cleaned_data, self.instance)

        return cleaned_data
