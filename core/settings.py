"""
Django settings for `RateMyModule` project.

Partially generated by "django-admin startproject" using Django 4.2.9.
"""

from collections.abc import Sequence

__all__: Sequence[str] = ("BASE_DIR", "LOG_LEVEL_CHOICES")

import inspect
import re
import sys
from pathlib import Path
from typing import Final

import django.urls
from environ import Env, FileAwareEnv, ImproperlyConfigured

from core.utils import MyPyEnv, reverse_url_with_get_params_lazy

# NOTE: Build paths inside the project like this: BASE_DIR / "subdir"
BASE_DIR: Path = Path(__file__).resolve().parent.parent


# NOTE: settings.py is parsed when setting up the mypy_django_plugin. When mypy runs, no environment variables are set, so they should not be accessed
IMPORTED_BY_MYPY_OR_CHECK_OR_MIGRATE: Final[bool] = (
    any(
        "mypy_django_plugin" in frame.filename
        for frame
        in inspect.stack()[1:]
        if not frame.filename.startswith("<")
    )
    or "check" in sys.argv
    or "migrate" in sys.argv
    or "makemigrations" in sys.argv
)
EnvClass: type[Env] = MyPyEnv if IMPORTED_BY_MYPY_OR_CHECK_OR_MIGRATE else FileAwareEnv  # type: ignore[no-any-unimported]

EnvClass.read_env(BASE_DIR / ".env")
env: Env = EnvClass(  # type: ignore[no-any-unimported]
    PRODUCTION=(bool, True),
    ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS=(int, 1)
)


# Production Vs Development settings

raw_log_level: str

if env("PRODUCTION"):
    # TODO(Matthew Norton): Add default `ALLOWED_HOSTS` & `ALLOWED_ORIGINS` once our group is given a domain from the Team Project module coordinators  # noqa: FIX002
    production_env: Env = EnvClass(  # type: ignore[no-any-unimported]
        ALLOWED_HOSTS=(list, []),
        ALLOWED_ORIGINS=(list, []),
        LOG_LEVEL=(str, "WARNING")
    )

    raw_log_level = production_env("LOG_LEVEL").upper().strip()

    # NOTE: Security Warning - Don't run with debug turned on in production!
    DEBUG = False

    ALLOWED_HOSTS = production_env("ALLOWED_HOSTS")
    ALLOWED_ORIGINS = production_env("ALLOWED_ORIGINS")
    CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS.copy()

else:
    development_env: Env = EnvClass(  # type: ignore[no-any-unimported]
        DEBUG=(bool, True),
        ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
        LOG_LEVEL=(str, "INFO")
    )

    raw_log_level = development_env("LOG_LEVEL").upper().strip()

    DEBUG = development_env("DEBUG")

    ALLOWED_HOSTS = development_env("ALLOWED_HOSTS")


# Environment Variables Validation

if env("SECRET_KEY").strip().lower() == "[replace with your generated secret key]":
    SECRET_KEY_NOT_SET_MESSAGE: Final[str] = (
        "Set the SECRET_KEY environment variable"
    )
    raise ImproperlyConfigured(SECRET_KEY_NOT_SET_MESSAGE)

LOG_LEVEL_CHOICES: Final[Sequence[str]] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
if raw_log_level not in LOG_LEVEL_CHOICES:
    INVALID_LOG_LEVEL_MESSAGE: Final[str] = (
        f"LOG_LEVEL must be one of {
            ",".join(f"{log_level_choice!r}" for log_level_choice in LOG_LEVEL_CHOICES[:-1])
        } or \"{
            LOG_LEVEL_CHOICES[-1]
        }\"."
    )
    raise ImproperlyConfigured(INVALID_LOG_LEVEL_MESSAGE)

if not env("ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS") > 0:
    INVALID_CONFIRMATION_EXPIRE_MESSAGE: Final[str] = (
        "ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS must be an integer greater than 0."
    )
    raise ImproperlyConfigured(INVALID_CONFIRMATION_EXPIRE_MESSAGE)

REPLACE_OAUTH_GOOGLE_CLIENT_ID_MESSAGE: Final[str] = (
    "[replace with your Google OAuth client ID]"
)
if env("OAUTH_GOOGLE_CLIENT_ID").strip().lower() == REPLACE_OAUTH_GOOGLE_CLIENT_ID_MESSAGE:
    OAUTH_GOOGLE_CLIENT_ID_NOT_SET_MESSAGE: Final[str] = (
        "Set the OAUTH_GOOGLE_CLIENT_ID environment variable"
    )
    raise ImproperlyConfigured(OAUTH_GOOGLE_CLIENT_ID_NOT_SET_MESSAGE)

OAUTH_GOOGLE_CLIENT_ID_IS_VALID: Final[bool] = bool(
    re.match(
        r"\A[0-9]{12}-[0-9a-z]{32}\.apps\.googleusercontent\.com\Z",
        env("OAUTH_GOOGLE_CLIENT_ID").strip()
    )
)
if not OAUTH_GOOGLE_CLIENT_ID_IS_VALID:
    INVALID_OAUTH_GOOGLE_CLIENT_ID_MESSAGE: Final[str] = (
        "OAUTH_GOOGLE_CLIENT_ID must be a valid Google OAuth client ID."
    )
    raise ImproperlyConfigured(INVALID_OAUTH_GOOGLE_CLIENT_ID_MESSAGE)

REPLACE_OAUTH_MICROSOFT_CLIENT_ID_MESSAGE: Final[str] = (
    "[replace with your Microsoft OAuth client ID]"
)
if env("OAUTH_MICROSOFT_CLIENT_ID").strip().lower() == REPLACE_OAUTH_MICROSOFT_CLIENT_ID_MESSAGE:  # noqa: E501
    OAUTH_MICROSOFT_CLIENT_ID_NOT_SET_MESSAGE: Final[str] = (
        "Set the OAUTH_MICROSOFT_CLIENT_ID environment variable"
    )
    raise ImproperlyConfigured(OAUTH_MICROSOFT_CLIENT_ID_NOT_SET_MESSAGE)

OAUTH_MICROSOFT_CLIENT_ID_IS_VALID: Final[bool] = bool(
    re.match(
        r"\A[0-9a-z]{8}-[0-9]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}\Z",
        env("OAUTH_MICROSOFT_CLIENT_ID").strip()
    )
)
if not OAUTH_MICROSOFT_CLIENT_ID_IS_VALID:
    INVALID_OAUTH_MICROSOFT_CLIENT_ID_MESSAGE: Final[str] = (
        "OAUTH_MICROSOFT_CLIENT_ID must be a valid Microsoft Graph OAuth client ID."
    )
    raise ImproperlyConfigured(INVALID_OAUTH_MICROSOFT_CLIENT_ID_MESSAGE)

if env("OAUTH_GOOGLE_SECRET").strip().lower() == "[replace with your Google OAuth secret]":
    OAUTH_GOOGLE_SECRET_NOT_SET_MESSAGE: Final[str] = (
        "Set the OAUTH_GOOGLE_SECRET environment variable"
    )
    raise ImproperlyConfigured(OAUTH_GOOGLE_SECRET_NOT_SET_MESSAGE)
if not re.match(r"\A[A-Z]{6}-[0-9A-Za-z]{28}\Z", env("OAUTH_GOOGLE_SECRET").strip()):
    INVALID_OAUTH_GOOGLE_SECRET_MESSAGE: Final[str] = (
        "OAUTH_GOOGLE_SECRET must be a valid Google OAuth secret."
    )
    raise ImproperlyConfigured(INVALID_OAUTH_GOOGLE_SECRET_MESSAGE)

REPLACE_OAUTH_MICROSOFT_SECRET_MESSAGE: Final[str] = (
    "[replace with your Microsoft OAuth secret]"
)
if env("OAUTH_MICROSOFT_SECRET").strip().lower() == REPLACE_OAUTH_MICROSOFT_SECRET_MESSAGE:
    OAUTH_MICROSOFT_SECRET_NOT_SET_MESSAGE: Final[str] = (
        "Set the OAUTH_MICROSOFT_SECRET environment variable"
    )
    raise ImproperlyConfigured(OAUTH_MICROSOFT_SECRET_NOT_SET_MESSAGE)
if not re.match(r"\A[0-9A-Za-z.~_-]{40}\Z", env("OAUTH_MICROSOFT_SECRET").strip()):
    INVALID_OAUTH_MICROSOFT_SECRET_MESSAGE: Final[str] = (
        "OAUTH_MICROSOFT_SECRET must be a valid Microsoft Graph OAuth secret."
    )
    raise ImproperlyConfigured(INVALID_OAUTH_MICROSOFT_SECRET_MESSAGE)


# Logging settings

# noinspection SpellCheckingInspection
LOGGING = {
    "version": 1,
    "formatters": {
        "ratemymodule": {
            "format": "[{asctime}] {name} | {levelname:^8} - {message}",
            "datefmt": "%d/%b/%Y %H:%M:%S",
            "style": "{"
        },
        "web_server": {
            "format": "[{asctime}] {message}",
            "datefmt": "%d/%b/%Y %H:%M:%S",
            "style": "{"
        }
    },
    "handlers": {
        "ratemymodule": {
            "class": "logging.StreamHandler",
            "formatter": "ratemymodule"
        },
        "web_server": {
            "class": "logging.StreamHandler",
            "formatter": "web_server"
        }
    },
    "loggers": {
        "django.server": {"handlers": ["web_server"], "level": raw_log_level}
    },
    "root": {"handlers": ["ratemymodule"], "level": raw_log_level}
}


# Web Server settings

ROOT_URLCONF = "core.urls"
# noinspection PyUnresolvedReferences
STATIC_ROOT = "staticfiles/"
STATIC_URL = "static/"
SECRET_KEY = env("SECRET_KEY").strip()  # NOTE: Security Warning - The secret key is used for important secret stuff (keep the one used in production a secret!)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SITE_ID = 1
WSGI_APPLICATION = "core.wsgi.APPLICATION"


# Application definition

# noinspection SpellCheckingInspection
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.microsoft",
    "allauth.socialaccount.providers.google",
    "ratemymodule.apps.RateMyModuleConfig",
    "api_htmx.apps.APIHTMXAppConfig",
    "web.apps.WebServerConfig",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.admindocs",
    "rangefilter"
]
# noinspection PyUnresolvedReferences
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware"
]


# Authentication Backend Settings

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend"
]


# Default URL Redirect Settings (used for authentication)

LOGIN_URL = reverse_url_with_get_params_lazy(
    "ratemymodule:home",
    get_params={"action": "login"}
)
LOGIN_REDIRECT_URL = django.urls.reverse_lazy("ratemymodule:home")
LOGOUT_REDIRECT_URL = django.urls.reverse_lazy("default")
SIGNUP_URL = reverse_url_with_get_params_lazy(
    "ratemymodule:home",
    get_params={"action": "signup"}
)


# Auth Model Settings

# TODO(Matthew Norton): Add user model  # noqa: FIX002
# AUTH_USER_MODEL = "ratemymodule.User"  # noqa: ERA001


# Authentication Configuration Settings (mainly for allauth & its associated packages)

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_USER_DISPLAY = lambda user: str(user)  # noqa: E731
ACCOUNT_USERNAME_MIN_LENGTH = 5
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = env("ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS")
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_FORMS = {
    "login": "ratemymodule.forms.Login_Form",
    "signup": "ratemymodule.forms.Signup_Form"
}
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "VERIFIED_EMAIL": True,
        "OAUTH_PKCE_ENABLED": True,
        "SCOPE": ["email"],
        "APP": {
            "name": "Google",
            "client_id": env("OAUTH_GOOGLE_CLIENT_ID").strip(),
            "secret": env("OAUTH_GOOGLE_SECRET").strip(),
            "key": ""
        }
    },
    "microsoft": {
        "VERIFIED_EMAIL": True,
        "OAUTH_PKCE_ENABLED": True,
        "SCOPE": ["email", "profile", "User.Read", "User.ReadBasic.All"],
        "APP": {
            "name": "Microsoft",
            "client_id": env("OAUTH_MICROSOFT_CLIENT_ID").strip(),
            "secret": env("OAUTH_MICROSOFT_SECRET").strip(),
            "key": "",
            "settings": {"tenant": "organizations"}
        }
    }
}


# Template settings

# noinspection PyUnresolvedReferences
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages"
            ]
        }
    }
]


# Database Settings

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "core.db"
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Internationalization, Language & Time settings

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True