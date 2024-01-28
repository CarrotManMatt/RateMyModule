"""
Util functions & classes within `core` app.

None of these functions or classes should depend on loaded apps or configured settings,
because this file is used before both of those operations are completed
(when settings are being loaded).
"""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "MyPyEnv",
    "reverse_url_with_get_params",
    "reverse_url_with_get_params_lazy"
)

import json
from collections.abc import Callable, Collection, Mapping
from pathlib import Path
from typing import TypeVar
from urllib.parse import urlparse

import django.urls
from django.http import QueryDict
from django.utils.functional import lazy
from environ import Env, FileAwareEnv, ImproperlyConfigured, environ

T = TypeVar("T")


class MyPyEnv(FileAwareEnv):  # type: ignore[no-any-unimported,misc]
    """Custom implementation of `Env` class that will not raise an error for invalid keys."""

    def get_value(self, var: str, cast: Callable[[object], T] | None = None, default: T | environ.NoValue = Env.NOTSET, parse_default: bool = False) -> T:  # type: ignore[no-any-unimported] # noqa: FBT001,FBT002,E501
        """
        Return value for given environment variable.

        If no Env variable value was set with the given name, return an arbitrary default value
        to prevent errors when type-checking with mypy.
        """
        try:
            return super().get_value(  # type: ignore[no-any-return]
                var=var,
                cast=cast,
                default=default,
                parse_default=parse_default
            )
        except ImproperlyConfigured:
            value: str
            if cast in (str, tuple, list, urlparse, None):
                value = "value"
            elif cast in (bool, int, float, json.loads):
                value = "0"
            elif cast == dict:
                value = "key,value"
            elif cast == Path:
                return Path()  # type: ignore[return-value]
            else:
                raise NotImplementedError from None

            return self.parse_value(  # type: ignore[no-any-return]
                value=value,
                cast=cast
            )


# noinspection SpellCheckingInspection
def reverse_url_with_get_params(viewname: Callable[[], str] | str | None = None, urlconf: str | None = None, args: Sequence[object] | None = None, kwargs: dict[str, object] | None = None, current_app: str | None = None, get_params: Mapping[str, object] | None = None) -> str:  # noqa: E501
    """Return a URL from the given view name, with the given get_params appended to the end."""
    url: str = django.urls.reverse(
        viewname=viewname,
        urlconf=urlconf,
        args=args,
        kwargs=kwargs,
        current_app=current_app
    )
    if not get_params:
        return url

    qdict: QueryDict = QueryDict("", mutable=True)

    key: str
    val: object
    for key, val in get_params.items():
        if isinstance(val, Collection) and not isinstance(val, str):
            qdict.setlist(key, list(val))
        else:
            qdict[key] = str(val)

    return url + "?" + qdict.urlencode()


reverse_url_with_get_params_lazy = lazy(reverse_url_with_get_params, str)
