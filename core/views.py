"""Views for direct use in `core` app."""

from collections.abc import Sequence

__all__: Sequence[str] = ("AdminDocsRedirectView",)

from typing import Final

import django.urls
from django.views.generic import RedirectView


class AdminDocsRedirectView(RedirectView):
    """Helper redirect view for the "docs/" url to" doc/" (with any included subpath)."""

    # noinspection SpellCheckingInspection
    def get_redirect_url(self, *reverse_args: object, subpath: str = "", **reverse_kwargs: object) -> str:  # noqa: E501
        """
        Return the URL redirect to.

        Keyword arguments from the URL pattern that is generating the redirect request
        are provided as kwargs to this method. Also adds a possible subpath
        to the end of the redirected URL.
        """
        if subpath:
            SUBPATH_ARGUMENT_IS_CONSISTENT: Final[bool] = bool(
                "subpath" in self.kwargs
                and isinstance(self.kwargs["subpath"], str)
            )
            if not SUBPATH_ARGUMENT_IS_CONSISTENT:
                INCONSISTENT_ARGUMENT_MESSAGE: Final[str] = (
                    f"Inconsistent argument {"subpath"!r} provided."
                )
                raise ValueError(INCONSISTENT_ARGUMENT_MESSAGE)

            subpath = self.kwargs.pop("subpath")

        # noinspection SpellCheckingInspection
        url: str = django.urls.reverse(
            "django-admindocs-docroot",
            args=reverse_args,
            kwargs=reverse_kwargs
        ) + subpath

        url_args: str = self.request.META.get("QUERY_STRING", "")
        if url_args and self.query_string:
            url = f"{url}?{url_args}"

        return url
