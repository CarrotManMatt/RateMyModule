"""Web HTML views for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = ("HomeView",)

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Main Dashboard view, for users to look at the most recent posts about uni modules."""

    template_name = "ratemymodule/home.html"
