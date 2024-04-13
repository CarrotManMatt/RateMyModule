from collections.abc import Sequence

# noinspection SpellCheckingInspection
__all__: Sequence[str] = ("get_module_search_url",)

import re

from django import template
from django.http import HttpRequest
from django.utils import html, safestring
from django.utils.safestring import SafeString

from ratemymodule.models import Module

register: template.Library = template.Library()


@register.filter(name="get_module_search_url", needs_autoescape=True, is_safe=True)
def get_module_search_url(module: object, request: object, *, autoescape: bool = True) -> SafeString:  # noqa: E501
    url: str = ""

    if isinstance(module, Module) and isinstance(request, HttpRequest):
        url = re.sub(
            r"&?action=[^&]*(?=&|$)",
            "",
            module.get_search_url(request=request),
            count=1,
        )

    if not autoescape:
        url = html.escape(url)

    return safestring.mark_safe(url)  # noqa: S308
