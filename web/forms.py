from collections.abc import Sequence

__all__: Sequence[str] = ("PostForm",)

from typing import override

from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from ratemymodule.models import Post


class PostForm(ModelForm):
    @staticmethod
    def generate_academic_year_choices():
        earliest_teaching_year = 2019
        latest_teaching_year = 2023
        academic_years = [
            year
            for year
            in range(earliest_teaching_year, latest_teaching_year + 1)
        ]
        choices = []
        for year in academic_years:
            next_year = year + 1
            year_str = str(year)
            next_year_str = str(next_year)
            academic_year_str = f"{year_str}-{next_year_str}"
            display_year_str = f"{year}/{next_year_str}"
            choices.append((academic_year_str, display_year_str))
        return choices

    academic_year_start = forms.ChoiceField(
        choices=generate_academic_year_choices(),
        required=True,
        label=_("Academic Year")
    )
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': _('Write your module review...')}),
        required=False,  # Not a required field
        label=_("Content")
    )
    overall_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(),
        required=True,
        label=_("Overall Rating")
    )
    difficulty_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(),
        required=False,
        label=_("Difficulty Rating")
    )
    assessment_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(),
        required=False,
        label=_("Assessment Rating")
    )
    teaching_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(),
        required=False,
        label=_("Teaching Rating")
    )

    @override
    def clean(self):
        cleaned_data = super().clean()
        for field in ("difficulty_rating", "assessment_rating", "teaching_rating"):
            if not cleaned_data[field]:
                cleaned_data.pop(field)

        cleaned_data["academic_year_start"] = int(cleaned_data["academic_year_start"].partition("-")[0])

        overall_rating = cleaned_data.get("overall_rating")
        if not overall_rating:
            self.add_error("overall_rating", _("This field is required."))
        return cleaned_data

    class Meta:
        model = Post
        fields = [
            "module",
            "academic_year_start",
            "content",
            "overall_rating",
            "difficulty_rating",
            "assessment_rating",
            "teaching_rating"
        ]
