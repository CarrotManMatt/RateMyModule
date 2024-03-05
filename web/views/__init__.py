"""Web HTML views for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = ("HomeView", "UserSettingsView")

from typing import override

from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from ratemymodule.models import Post
from web.views import graph_utils


class HomeView(TemplateView):
    """Main Dashboard view, for users to look at the most recent posts about uni modules."""

    template_name = "ratemymodule/home.html"

    @override
    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context_data: dict[str, object] = super().get_context_data(**kwargs)

        if not Post.objects.exists():
            context_data.update(
                {
                    "overall_rating_bar_graph": "",
                    "difficulty_bar_graph": "",
                    "teaching_graph": "",
                    "assessment_graph": ""
                }
            )

        else:
            context_data.update(
                {
                    "overall_rating_bar_graph": mark_safe(  # noqa: S308
                        graph_utils.overall_rating_bar_graph()
                    ),
                    "difficulty_bar_graph": mark_safe(  # noqa: S308
                        graph_utils.difficulty_rating_bar_graph()
                    ),
                    "teaching_graph": mark_safe(graph_utils.teaching_quality_bar_graph()),  # noqa: S308
                    "assessment_graph": mark_safe(graph_utils.assessment_quality_bar_graph())  # noqa: S308
                }
            )

        return context_data


class UserSettingsView(TemplateView):
    """Account management view, for users to edit their account settings."""

    template_name = "ratemymodule/user-settings.html"
