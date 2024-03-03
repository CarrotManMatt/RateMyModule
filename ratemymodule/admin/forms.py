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
    @override
    def clean(self) -> dict[str, object] | None:
        cleaned_data: dict[str, object] | None = super().clean()

        if cleaned_data:
            is_staff: object = cleaned_data["is_staff"]
            if not isinstance(is_staff, bool):
                raise TypeError

            is_superuser: object = cleaned_data["is_superuser"]
            if not isinstance(is_superuser, bool):
                raise TypeError

            if is_superuser:
                cleaned_data["is_staff"] = True

            enrolled_course_set: object = cleaned_data["enrolled_course_set"]
            if not isinstance(enrolled_course_set, QuerySetAny):
                raise TypeError

            # noinspection PyUnresolvedReferences
            if not (is_staff or is_superuser) and not enrolled_course_set.exists():
                raise ValidationError(
                    {"enrolled_course_set": "This field is required."},
                    code="required"
                )

            USER_HAS_POSTS_ABOUT_MODULES_ON_REMOVED_COURSES: Final[bool] = (
                bool(self.instance.pk)
                and Post.objects.filter(
                    user=self.instance,
                    module__course_set__pk__in=self.instance.enrolled_course_set.exclude(
                        pk__in=enrolled_course_set
                    )
                ).exists()
            )
            if USER_HAS_POSTS_ABOUT_MODULES_ON_REMOVED_COURSES:
                raise ValidationError(
                    {
                        "enrolled_course_set": _(
                            "Courses cannot be removed from a user if they have made posts "
                            "about modules attached to that course."
                        )
                    },
                    code="invalid"
                )

            email: object = cleaned_data["email"]
            if not isinstance(email, str):
                raise TypeError

            try:
                # noinspection PyUnresolvedReferences,PyProtectedMember
                USER_COURSES_IN_MULTIPLE_UNIVERSITIES: Final[bool] = (
                    enrolled_course_set.exclude(
                        university=self.instance._get_university_from_email_domain(  # noqa: SLF001
                            email.rpartition("@")[2],
                            is_staff=any((is_staff, is_superuser))
                        )
                    ).exists()
                )

            except University.DoesNotExist:
                pass

            else:
                if USER_COURSES_IN_MULTIPLE_UNIVERSITIES:
                    raise ValidationError(
                        {
                            "enrolled_course_set": _(
                                "A user cannot be enrolled in courses "
                                "across multiple universities."
                            )
                        },
                        code="invalid"
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
            post.liked_user_set.set(self.cleaned_data["liked_user_set"])
            post.disliked_user_set.set(self.cleaned_data["disliked_user_set"])
            self.save_m2m()

        return post

    @override
    def clean(self) -> dict[str, object] | None:
        cleaned_data: dict[str, object] | None = super().clean()

        if cleaned_data:
            module: object = cleaned_data["module"]
            if not isinstance(module, Module):
                raise TypeError

            user: object = cleaned_data["user"]
            if not isinstance(user, User):
                raise TypeError

            # NOTE: This error should only be raised from the form clean if it was the many-to-many connection that changed (not if the user changed)
            POST_IS_ABOUT_MODULE_USER_HAS_NOT_TAKEN: Final[bool] = (
                (not self.instance.pk or user == self.instance.user)
                and module not in user.module_set.all()
            )
            if POST_IS_ABOUT_MODULE_USER_HAS_NOT_TAKEN:
                raise ValidationError(
                    {
                        "module": _(
                            "You cannot create posts about modules that you have not taken."
                        )
                    },
                    code="invalid"
                )

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
            course.module_set.set(self.cleaned_data["module_set"])
            course.enrolled_user_set.set(self.cleaned_data["enrolled_user_set"])
            self.save_m2m()

        return course

    @override
    def clean(self) -> dict[str, object] | None:
        cleaned_data: dict[str, object] | None = super().clean()

        if cleaned_data:
            module_set: object = cleaned_data["module_set"]
            if not isinstance(module_set, QuerySetAny):
                raise TypeError

            enrolled_user_set: object = cleaned_data["enrolled_user_set"]
            if not isinstance(enrolled_user_set, QuerySetAny):
                raise TypeError

            university: object = cleaned_data["university"]
            if not isinstance(university, University):
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

            if self.instance.pk:
                REMOVED_MODULES_HAVE_POSTS_MADE_ABOUT_THEM_BY_ENROLLED_USERS: Final[bool] = (
                    Post.objects.filter(
                        module__pk__in=self.instance.module_set.exclude(pk__in=module_set)
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

                REMOVED_USERS_HAVE_MADE_POSTS_ABOUT_ATTACHED_MODULES: Final[bool] = (
                    Post.objects.filter(
                        user__pk__in=self.instance.enrolled_user_set.exclude(
                            pk__in=enrolled_user_set
                        )
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

                no_courses_module: Module
                for no_courses_module in self.instance.module_set.exclude(pk__in=module_set):
                    if not no_courses_module.course_set.exclude(pk=self.instance.pk).exists():
                        raise ValidationError(
                            {
                                "module_set": _(
                                    "Modules cannot be removed from this course "
                                    "if they are not attached to any other courses."
                                )
                            },
                            code="required"
                        )

                REMOVED_ENROLLED_USERS: Iterable[User] = (
                    self.instance.enrolled_user_set.exclude(
                        pk__in=enrolled_user_set
                    )
                )

                no_enrolled_courses_user: User
                for no_enrolled_courses_user in REMOVED_ENROLLED_USERS:
                    USER_WOULD_HAVE_NO_COURSES: bool = (
                        not no_enrolled_courses_user.enrolled_course_set.exclude(
                            pk=self.instance.pk
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

        return cleaned_data


class ModuleModelForm(DjangoModelForm[Module]):
    """Custom form to edit the details of a `Module` object within the admin interface."""

    @override
    def clean(self) -> dict[str, object] | None:
        cleaned_data: dict[str, object] | None = super().clean()

        if cleaned_data:
            try:
                course_set: object = cleaned_data["course_set"]
            except KeyError:
                pass
            else:
                if not isinstance(course_set, QuerySetAny):
                    raise TypeError

                # noinspection PyUnresolvedReferences
                if not course_set.exists():
                    raise ValidationError(
                        {"course_set": _("This field is required.")},
                        code="required"
                    )

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

                MODULE_HAS_POSTS_FROM_USERS_ON_REMOVED_COURSES: Final[bool] = (
                    bool(self.instance)
                    and Post.objects.filter(
                        module=self.instance,
                        user__enrolled_course_set__pk__in=self.instance.course_set.exclude(
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

                # noinspection PyUnresolvedReferences
                university: University = course_set.all()[0].university

                name: object = cleaned_data["name"]
                if not isinstance(name, str):
                    raise TypeError

                same_name_module_set: QuerySet[Module] = university.module_set.filter(
                    name=name
                )

                if self.instance.pk:
                    same_name_module_set = same_name_module_set.exclude(pk=self.instance.pk)

                if same_name_module_set.exists():
                    raise ValidationError(
                        _("A module with this name already exists at %(university)s."),
                        params={"university": university},
                        code="unique"
                    )

                code: object = cleaned_data["code"]
                if not isinstance(code, str):
                    raise TypeError

                same_code_module_set: QuerySet[Module] = university.module_set.filter(
                    code=code
                )

                if self.instance.pk:
                    same_code_module_set = same_code_module_set.exclude(pk=self.instance.pk)

                if same_code_module_set.exists():
                    raise ValidationError(
                        _(
                            "A module with this reference code already exists "
                            "at %(university)s."
                        ),
                        params={"university": university},
                        code="unique"
                    )

        return cleaned_data
