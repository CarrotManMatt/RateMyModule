from collections.abc import Sequence

__all__: Sequence[str] = ("PostForm", "SignupForm")

from typing import Final, override

from allauth.account.forms import SignupForm as AllAuthSignupForm
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from ratemymodule.models import Post, User


class PostForm(ModelForm[Post]):
    ACADEMIC_YEAR_CHOICES: Final[Sequence[tuple[int, str]]] = [
        (year, f"{year}/{year + 1}")
        for year
        in range(2019, 2023 + 1)
    ]

    academic_year_start = forms.TypedChoiceField(
        choices=ACADEMIC_YEAR_CHOICES,
        required=True,
        coerce=int,
        label=_("Academic Year"),
    )
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": _("Write your module review...")}),
        required=False,  # Not a required field
        label=_("Content"),
    )
    overall_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(),
        required=True,
        label=_("Overall Rating"),
    )
    difficulty_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(),
        required=False,
        label=_("Difficulty Rating"),
    )
    assessment_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(),
        required=False,
        label=_("Assessment Rating"),
    )
    teaching_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(),
        required=False,
        label=_("Teaching Rating"),
    )

    @override
    def clean(self) -> dict[str, object] | None:
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
        for field in ("difficulty_rating", "assessment_rating", "teaching_rating"):
            if not cleaned_data[field]:
                cleaned_data.pop(field)

        overall_rating = cleaned_data.get("overall_rating")
        if not overall_rating:
            self.add_error("overall_rating", _("This field is required."))
        return cleaned_data

    class Meta:
        model = Post
        fields = (
            "module",
            "academic_year_start",
            "content",
            "overall_rating",
            "difficulty_rating",
            "assessment_rating",
            "teaching_rating",
        )


class SignupForm(AllAuthSignupForm):
    @override
    def clean(self) -> dict[str]:
        super().clean()

        non_empty_fields: set[str] = set()
        field_name: str
        for field_name in self.fields:
            if field_name != "password2" and self.cleaned_data.get(field_name):
                non_empty_fields.add(field_name)

        try:
            User(
                email=self.cleaned_data.get("email"),
                password=self.cleaned_data.get("password1")
            ).full_clean()
        except ValidationError as e:
            self.add_errors_from_validation_error_exception(e, non_empty_fields)

        if self.errors.get("password1") and any("common" in error for error in self.errors["password1"]) and any("short" in error for error in self.errors["password1"]):
            self._errors["password1"] = [error for error in self._errors["password1"] if "common" not in error]

        return self.cleaned_data
