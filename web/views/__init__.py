"""Web HTML views for `RateMyModule` project."""

from collections.abc import Sequence

__all__: Sequence[str] = ("HomeView",)

from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name: str = "ratemymodule/home.html"
