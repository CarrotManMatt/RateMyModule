"""Validators used by models within the `ratemymodule` app."""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "HTML5EmailValidator",
    "FreeEmailValidator",
    "ExampleEmailValidator",
    "PreexistingEmailTLDValidator",
    "ConfusableEmailValidator",
    "UnicodePropertiesRegexValidator",
)

import re as regex
from collections.abc import Collection
from typing import Final, override

import regex as full_regex
import tldextract
from confusable_homoglyphs import confusables
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.utils import deconstruct
from django.utils.translation import gettext_lazy as _

deconstructible = deconstruct.deconstructible


@deconstructible
class HTML5EmailValidator(RegexValidator):
    """Validator that applies HTML5's email address rules."""

    # SOURCE: WHATWG HTML5 spec, section 4.10.5.1.5.
    HTML5_EMAIL_RE: str = (
        r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]"
        r"+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}"
        r"[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]"
        r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )

    message = EmailValidator.message
    regex = regex.compile(HTML5_EMAIL_RE)


@deconstructible
class FreeEmailValidator:
    """Validator disallowing common temporary/free email services as email address domains."""

    # noinspection SpellCheckingInspection
    DEFAULT_FREE_EMAIL_DOMAINS: Final[frozenset[str]] = frozenset(
        {
            "decabg.eu",
            "gufum.com",
            "ema-sofia.eu",
            "dropsin.net",
            "finews.biz",
            "triots.com",
            "rungel.net",
            "jollyfree.com",
            "gotgel.org",
            "prolug.com",
            "tmail1.com",
            "tmail.com",
            "tempmail.com",
            "tmail2.com",
            "tmail3.com",
            "tmail4.com",
            "tmail5.com",
            "tmail6.com",
            "tmail7.com",
            "tmail8.com",
            "tmail9.com",
            "lyricspad.net",
            "lyft.live",
            "dewareff.com",
            "kaftee.com",
            "letpays.com",
        },
    )

    @override
    def __init__(self, free_email_domains: Collection[str] | None = None) -> None:
        """Initialise a new specific instance of this validator with the given domains."""
        self.free_email_domains = (
            self.DEFAULT_FREE_EMAIL_DOMAINS
            if free_email_domains is None
            else set(free_email_domains)
        )

    def __call__(self, value: object) -> None:
        """Execute this validator to decide whether the given value is valid."""
        if not isinstance(value, str):
            return

        if value.count("@") != 1:
            return

        if value.rpartition("@")[2] in self.free_email_domains:
            raise ValidationError(
                {
                    "email": _(
                        "Registration using free email addresses is prohibited. "
                        "Please supply a different email address."  # noqa: COM812
                    ),
                },
                code="invalid",
            )

    @override
    def __eq__(self, other: object) -> bool:
        """Check whether this validator is the same as another given validator."""
        if not hasattr(other, "free_email_domains"):
            return NotImplemented

        # noinspection PyUnresolvedReferences
        return bool(self.free_email_domains == other.free_email_domains)


@deconstructible
class ExampleEmailValidator:
    """Validator that disallows common example address domain values."""

    DEFAULT_EXAMPLE_EMAIL_DOMAINS: Final[frozenset[str]] = frozenset({"example", "test"})

    @override
    def __init__(self, example_email_domains: Collection[str] | None = None) -> None:
        """Initialise a new specific instance of this validator with the given domains."""
        self.example_email_domains = (
            self.DEFAULT_EXAMPLE_EMAIL_DOMAINS
            if example_email_domains is None
            else set(example_email_domains)
        )

    def __call__(self, value: object) -> None:
        """Execute this validator to decide whether the given value is valid."""
        if not isinstance(value, str):
            return

        if value.count("@") != 1:
            return

        if tldextract.extract(value.rpartition("@")[2]).domain in self.example_email_domains:
            raise ValidationError(
                {
                    "email": _(
                        "Registration using unresolvable example email addresses "
                        "is prohibited. Please supply a different email address."  # noqa: COM812
                    ),
                },
                code="invalid",
            )


@deconstructible
class PreexistingEmailTLDValidator:
    """Deprecated! DO NOT USE!"""

    def __call__(self, _: object) -> None:
        """Execute this validator to decide whether the given value is valid."""
        raise DeprecationWarning


@deconstructible
class ConfusableEmailValidator:
    """
    Validator which disallows 'dangerous' email addresses likely to contain homograph attacks.

    An email address is "dangerous" if either the local-part or the domain,
    considered on their own, are mixed-script and contain one or more characters
    appearing in the Unicode Visually Confusable Characters file.
    """

    def __call__(self, value: object) -> None:
        """Execute this validator to decide whether the given value is valid."""
        if not isinstance(value, str):
            return

        if value.count("@") != 1:
            return

        local: str
        domain: str
        local, __, domain = value.rpartition("@")

        if confusables.is_dangerous(local) or confusables.is_dangerous(domain):
            raise ValidationError(
                {
                    "email": _(
                        "This email address cannot be registered. "
                        "Please supply a different email address."  # noqa: COM812
                    ),
                },
                code="invalid",
            )


@deconstructible
class UnicodePropertiesRegexValidator(RegexValidator):
    """Validator that validates a given string against a regex that includes unicode props."""

    # noinspection PyShadowingNames
    @override
    def __init__(self, regex: str, message: str | None = None, *, code: str | None = None, inverse_match: bool | None = None, flags: regex.RegexFlag | None = None) -> None:  # noqa: E501
        super().__init__(
            regex=full_regex.compile(regex),  # type: ignore[arg-type]
            message=message,
            code=code,
            inverse_match=inverse_match,
            flags=flags,
        )
