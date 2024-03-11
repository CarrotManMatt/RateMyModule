from collections.abc import Sequence

__all__: Sequence[str] = ("PostForm",)

from typing import Final, override

from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from ratemymodule.models import Post


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
