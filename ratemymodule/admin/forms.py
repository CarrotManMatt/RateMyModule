"""Custom forms to edit the details of models within the admin interface."""

from collections.abc import Sequence

__all__: Sequence[str] = ("UserChangeForm",)

from typing import override

from django import forms
from django.contrib.admin import widgets as admin_widgets
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.utils.translation import gettext_lazy as _

from ratemymodule.models import Course, User


class UserChangeForm(DjangoUserChangeForm[User]):
    """Custom form to edit the details of a `User` object within the admin interface."""

    enrolled_courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=True,
        widget=admin_widgets.FilteredSelectMultiple(
            verbose_name=_("Enrolled Courses"),
            is_stacked=False
        ),
        help_text=_(
            "The set of courses that this user has enrolled in. "
            "(Hold down “Control”, or “Command” on a Mac, to select more than one.)"
        )
    )

    @override
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["enrolled_courses"].initial = self.instance.enrolled_course_set.all()

    @override
    def save(self, commit: bool = True) -> User:
        user: User = super().save(commit=False)

        if commit:
            user.save()

        if user.pk:
            user.enrolled_course_set.set(self.cleaned_data["enrolled_courses"])
            self.save_m2m()

        return user
