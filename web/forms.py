"""Contains forms for getting data from the user of RateMyModule."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "AnalyticsForm",
    "PostForm",
    "SignupForm",
    "ChangeCoursesForm",
    "ReportForm",
)

from collections.abc import Iterable
from typing import Final, override

from allauth.account.forms import SignupForm as AllAuthSignupForm
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from ratemymodule.models import Course, Post, Report, User


class ChangeCoursesForm(ModelForm[User]):
    """The form for getting the data to change courses for a user."""

    enrolled_course_set = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "autocomplete"}),
        required=True,
    )

    class Meta:  # noqa: D106
        model = User
        fields = ("enrolled_course_set",)


class PostForm(ModelForm[Post]):
    """The form for getting the data for a post from a user."""

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
    tool_tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "autocomplete"}),
    )
    topic_tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "autocomplete"}),
    )
    other_tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "autocomplete"}),
    )

    class Meta:  # noqa: D106
        model = Post
        fields = (
            "module",
            "academic_year_start",
            "content",
            "overall_rating",
            "difficulty_rating",
            "assessment_rating",
            "teaching_rating",
            "tool_tags",
            "topic_tags",
            "other_tags",
        )

    @override
    def clean(self) -> dict[str, object] | None:
        cleaned_data: dict[str, object] | None = super().clean()

        if not cleaned_data:
            return cleaned_data

        # Check if the difficulty, assessment and teaching ratings are present
        for field in ("difficulty_rating", "assessment_rating", "teaching_rating"):
            if not cleaned_data.get(field):
                cleaned_data.pop(field, None)

        # Check if the overall rating is present
        if "overall_rating" not in cleaned_data:
            self.add_error("overall_rating", _("This field is required."))

        # Clean the tags
        for field in ("tool_tags", "topic_tags", "other_tags"):
            tag_data: object | None = cleaned_data.get(field, None)
            tag_items: Iterable[str] = (
                tag_data.split(",")
                if isinstance(tag_data, str)
                else tag_data if isinstance(tag_data, Iterable) else ()
            )
            cleaned_tags = []
            for item in tag_items:
                stripped_item = item.strip()
                if stripped_item.startswith("custom-"):
                    tag_name = stripped_item[7:].strip()
                    cleaned_tags.append(tag_name)
                else:
                    cleaned_tags.append(stripped_item)
            cleaned_data[field] = cleaned_tags

        return cleaned_data


class ReportForm(forms.ModelForm[Report]):
    reason = forms.ChoiceField(
        choices=Report.Reasons.choices,
        widget=forms.RadioSelect(),
        required=True,
        label="Reason",
    )
    post_pk = forms.IntegerField()

    class Meta:  # noqa: D106
        model = Report
        fields = ("reason", "post_pk")


class SignupForm(AllAuthSignupForm):  # type: ignore[misc,no-any-unimported]
    """The form for signing up a new user."""

    # Overriding the __init__ method to set placeholders
    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize the signup form with password and email widgets."""
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs["placeholder"] = "University Email Address"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm Password"

        for field_name in self.fields:
            self.fields[field_name].label = ""

    @override
    def clean(self) -> dict[str, object]:  # type: ignore[misc]
        super().clean()

        non_empty_fields: set[str] = set()
        field_name: str
        for field_name in self.fields:
            if field_name != "password2" and self.cleaned_data.get(field_name):
                non_empty_fields.add(field_name)

        try:
            User(
                email=self.cleaned_data.get("email"),
                password=self.cleaned_data.get("password1"),
            ).full_clean()
        except ValidationError as e:
            self.add_errors_from_validation_error_exception(e, non_empty_fields)

        HAS_PASSWORD_ERRORS: Final[bool] = (
            self.errors.get("password1")
            and any("common" in error for error in self.errors["password1"])
            and any("short" in error for error in self.errors["password1"])
        )
        if HAS_PASSWORD_ERRORS:
            self._errors["password1"] = [
                error
                for error
                in self._errors["password1"]
                if "common" not in error
            ]

        return self.cleaned_data  # type: ignore[no-any-return]


class AnalyticsForm(forms.Form):
    """get the data to make the advanced analytics graph."""

    aa_difficulty_rating = forms.BooleanField(
        label="Difficulty Rating?",
        required=False,
    )
    aa_overall_rating = forms.BooleanField(
        label="Overall Rating?",
        required=False,
    )
    aa_teaching_quality = forms.BooleanField(
        label="Teaching Quality?",
        required=False,
    )
    aa_assessment_quality = forms.BooleanField(
        label="Assessment Quality?",
        required=False,
    )
    aa_start_year = forms.IntegerField(
        label="From year?",
        widget=forms.TextInput(),
    )
    aa_start_year.widget.attrs.update({
        "class": "year-input-box",
        "type": "text",
        "id": "id_start_year",
    })
    aa_end_year = forms.IntegerField(
        label="To year?",
        widget=forms.TextInput(),
    )
    aa_end_year.widget.attrs.update({
        "class": "year-input-box",
        "type": "text",
        "id": "id_end_year",
    })
