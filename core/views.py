"""Views for direct use in `core` app."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "AdminDocsRedirectView",
    "AdminLoginRedirectView",
)

import abc
from typing import Final, override

import django.urls
from django.conf import settings
from django.http import QueryDict
from django.views.generic import RedirectView


class _BaseAdminDocsRedirectView(RedirectView, abc.ABC):
    """Helper redirect view for a given pattern name (with any included sub-path)."""

    @abc.abstractmethod
    def _get_core_url(self, reverse_args: tuple[object, ...], reverse_kwargs: dict[str, object]) -> str:  # noqa: E501
        """Get the core URL to redirect to."""

    # noinspection PyMethodMayBeStatic
    def _add_additional_params(self, get_params: QueryDict) -> QueryDict:
        return get_params

    # noinspection SpellCheckingInspection
    @override
    def get_redirect_url(self, *reverse_args: object, subpath: str = "", **reverse_kwargs: object) -> str:  # noqa: E501
        """
        Return the URL to redirect to.

        Keyword arguments from the URL pattern that is generating the redirect request
        are provided as kwargs to this method.
        Also adds a possible sub-path to the end of the redirected URL.
        """
        if subpath:
            SUBPATH_ARGUMENT_IS_CONSISTENT: Final[bool] = bool(
                "subpath" in self.kwargs
                and isinstance(self.kwargs["subpath"], str)  # noqa: COM812
            )
            if not SUBPATH_ARGUMENT_IS_CONSISTENT:
                INCONSISTENT_ARGUMENT_MESSAGE: Final[str] = (
                    f"Inconsistent argument {"subpath"!r} provided."
                )
                raise ValueError(INCONSISTENT_ARGUMENT_MESSAGE)

            subpath = self.kwargs.pop("subpath")

        url: str = self._get_core_url(reverse_args, reverse_kwargs)
        if "?" in url:
            GET_PARAMS_IN_PATH_MESSAGE: Final[str] = (
                "Simple path must not contain GET parameters."
            )
            raise ValueError(GET_PARAMS_IN_PATH_MESSAGE)

        url += subpath

        get_params: QueryDict = QueryDict(
            self.request.META.get("QUERY_STRING", ""),
            mutable=True,
        )
        get_params = self._add_additional_params(get_params)

        return f"{url}?{get_params.urlencode()}" if get_params else url


class AdminDocsRedirectView(_BaseAdminDocsRedirectView):
    """Helper redirect view for the "docs/" URL to "doc/" (with any included sub-path)."""

    @override
    def _get_core_url(self, reverse_args: tuple[object, ...], reverse_kwargs: dict[str, object]) -> str:  # noqa: E501
        # noinspection SpellCheckingInspection
        return django.urls.reverse(
            viewname="django-admindocs-docroot",
            args=reverse_args,
            kwargs=reverse_kwargs,
        )


class AdminLoginRedirectView(_BaseAdminDocsRedirectView):
    """Helper redirect view for the "admin/login/" URL (with any included sub-path)."""

    @override
    def __init__(self) -> None:
        original_path: str
        original_params: str
        original_path, _, original_params = settings.LOGIN_URL.partition("?")

        self._CORE_URL: Final[str] = original_path
        self._CORE_PARAMS: QueryDict = QueryDict(original_params, mutable=False)

        super().__init__()

    @override
    def _get_core_url(self, reverse_args: tuple[object, ...], reverse_kwargs: dict[str, object]) -> str:  # noqa: E501
        return self._CORE_URL

    @override
    def _add_additional_params(self, get_params: QueryDict) -> QueryDict:
        get_params.update(self._CORE_PARAMS)  # type: ignore[arg-type]
        get_params.setdefault("next", "/admin/")
        return get_params
