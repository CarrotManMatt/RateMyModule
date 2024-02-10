# Project Structure

## Quick Links

- [Top Level Files](#top-level-files)
- [Top-Level Python Packages](#top-level-python-packages)
- [Core](#core)
- [RateMyModule](#ratemymodule)
- [Web](#web)
- [HTMX API](#htmx-api)
- [REST API](#rest-api)

## Top Level Files

- [`manage.py`](/manage.py): Runs as a command-line utility to perform administrative tasks.
(See [the Django documentation about `manage.py`](https://docs.djangoproject.com/en/4.2/ref/django-admin))
- [`pyproject.toml`](/pyproject.toml): Orchestrates project metadata & dependencies.
(See [Poetry's documentation](https://python-poetry.org/docs/pyproject))
- [`.env.example`](/.env.example): List of every environment variable setting
that can be configured when deploying this project.
This file can be renamed to `.env` in deployment (along with changing the necessary settings),
to enable customisation of the deployment settings

## Top-Level Python Packages

Each top-level Python package is configured as a [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications).
Every top-level Python package will have an `__init__.py` file
containing the standard [`__all__` declaration](https://stackoverflow.com/a/64130/14403974).
However, this [`__all__` declaration](https://stackoverflow.com/a/64130/14403974)
should be empty, as Django apps should not export any objects directly.

- [`core`](/core): The core [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
that includes the configuration for the [project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)'s
webserver as a whole
- [`ratemymodule`](/ratemymodule): The primary [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
that defines the database models & request independent [CRUD](https://codecademy.com/article/what-is-crud)
actions
- [`web`](/web): The main HTML web server [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
that encompasses how to respond to [web requests](https://docs.djangoproject.com/en/4.2/topics/http)
sent to this [Django project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
- [`api_htmx`](/api_htmx): The [HTMX](https://htmx.org) API [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
that defines how to respond to [HTMX](https://htmx.org) [AJAX](https://wikipedia.org/wiki/Ajax_(programming))
[requests](https://docs.djangoproject.com/en/4.2/topics/http) from web-based users
- [`api_rest`](/api_rest): The [REST](https://wikipedia.org/wiki/REST) API [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
that defines how to respond to [JSON](https://json.org) [API](https://wikipedia.org/wiki/API)
[requests](https://docs.djangoproject.com/en/4.2/topics/http) from [third-party API](https://wikipedia.org/wiki/Open_API)
users

## Core

- [`settings.py`](/core/settings.py): Contains the all configurations
for the entirety of this [Django project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications).
(See [Django's settings documentation](https://docs.djangoproject.com/en/4.2/topics/settings))
- [`urls.py`](/core/urls.py): The core [URL dispatcher](https://docs.djangoproject.com/en/4.2/topics/http/urls)
entry point, which defines how to traverse to every other [app's individual URL dispatcher](https://docs.djangoproject.com/en/4.2/topics/http/urls#including-other-urlconfs).
(See [Django's URL dispatcher documentation](https://docs.djangoproject.com/en/4.2/topics/http/urls))
- [`utils.py`](/core/utils.py): Contains common utility functions & classes,
used within the `core` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications).
These must all be [lazily loaded](https://docs.djangoproject.com/en/4.2/topics/performance/#understanding-laziness)
because they are imported before any of the [Django apps](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
have been set up.
(I.e. **Do not import any objects from any of the [Django apps](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)**)
- [`views.py`](/core/views.py): Contains any simplistic [views](https://docs.djangoproject.com/en/4.2/topics/http/views)
used directly within [`core/urls.py`](/core/urls.py)
- [`wsgi.py`](/core/wsgi.py): Defines how WSGI webservers can process incoming [web requests](https://docs.djangoproject.com/en/4.2/topics/http)
with this [Django project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications).
This has been automatically generated and is unlikely to need to be changed

## RateMyModule

- [`models/__init__.py`](/ratemymodule/models/__init__.py):
Holds the definition for every [DB model](https://docs.djangoproject.com/en/4.2/topics/db/models)
used in this [Django project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications),
alongside any request independent [CRUD](https://codecademy.com/article/what-is-crud) actions,
relating to each [model](https://docs.djangoproject.com/en/4.2/topics/db/models)
- [`models/utils.py`](/ratemymodule/models/utils.py):
Contains common utility functions & classes used by the definition of [models](https://docs.djangoproject.com/en/4.2/topics/db/models)
within [`models/__init__.py`](/ratemymodule/models/__init__.py)
- [`admin/__init__.py`](/ratemymodule/admin/__init__.py): Defines how to display the [models](https://docs.djangoproject.com/en/4.2/topics/db/models),
inside this [Django project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications),
on the [automatic admin UI](https://docs.djangoproject.com/en/4.2/ref/contrib/admin) pages
- [`migrations/`](/ratemymodule/migrations): Contains auto-generated [database migrations](https://docs.djangoproject.com/en/4.2/topics/migrations)
([one migration per file](https://docs.djangoproject.com/en/4.2/topics/migrations#migration-files)).
These are used by [Django's database engine](https://docs.djangoproject.com/en/4.2/ref/databases)
to ensure that the database matches the model definitions
specified within [`models/__init__.py`](/ratemymodule/models/__init__.py)
- [`tests/`](/ratemymodule/tests): Collection of [unit-tests](https://wikipedia.org/wiki/Unit_testing)
to ensure all functionality defined within the `ratemymodule` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
works as expected.
(See [Django's testing documentation](https://docs.djangoproject.com/en/4.2/topics/testing))
- [`apps.py`](/ratemymodule/apps.py): Contains the [configuration classes](https://docs.djangoproject.com/en/4.2/ref/applications#application-configuration)
to provide metadata about the `ratemymodule` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)

## Web

- [`views/`](/web/views): Contains files that in-turn contain collections of [views](https://docs.djangoproject.com/en/4.2/topics/http/views)
to respond to [HTTP requests](https://docs.djangoproject.com/en/4.2/topics/http)
associated with the primary web request responder
- [`apps.py`](/web/apps.py): Contains the [configuration classes](https://docs.djangoproject.com/en/4.2/ref/applications#application-configuration)
to provide metadata about the `web` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
- [`urls.py/`](/web/urls.py): Contains the list of URLs available to the primary web server
[URL dispatcher](https://docs.djangoproject.com/en/4.2/topics/http/urls)
- [`tests/`](/web/tests): Collection of [unit-tests](https://wikipedia.org/wiki/Unit_testing)
to ensure all functionality defined within the `web` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
works as expected.
(See [Django's testing documentation](https://docs.djangoproject.com/en/4.2/topics/testing))
- [`templates/ratemymodule/`](/web/templates/ratemymodule): Contains [HTML](https://wikipedia.org/wiki/HTML)-style
[Django templates](https://docs.djangoproject.com/en/4.2/topics/templates)
that are populated with the necessary [context data](https://docs.djangoproject.com/en/4.2/topics/class-based-views/generic-display#adding-extra-context),
then sent as the final [HTML response](https://docs.djangoproject.com/en/4.2/ref/template-response)
to an [HTTP web request](https://docs.djangoproject.com/en/4.2/topics/http)
- [`static/ratemymodule/`](/web/static/ratemymodule): Contains all [static files](https://docs.djangoproject.com/en/5.0/howto/static-files)
that are served alongside [HTML](https://docs.djangoproject.com/en/4.2/ref/template-response)
[web requests]((https://docs.djangoproject.com/en/4.2/topics/http)).
(E.g. image, [CSS](https://wikipedia.org/wiki/CSS) & [JS](https://wikipedia.org/wiki/JavaScript)
files)

## HTMX API

- [`views/`](/api_htmx/views): Contains files that in-turn contain collections of [views](https://docs.djangoproject.com/en/4.2/topics/http/views)
to respond to [HTTP requests](https://docs.djangoproject.com/en/4.2/topics/http)
associated with the [HTMX API](https://htmx.org/docs#ajax)
- [`apps.py`](/api_htmx/apps.py): Contains the [configuration classes](https://docs.djangoproject.com/en/4.2/ref/applications#application-configuration)
to provide metadata about the `api_htmx` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
- [`urls.py/`](/api_htmx/urls.py): Contains the list of URLs available to the HTMX API [URL dispatcher](https://docs.djangoproject.com/en/4.2/topics/http/urls)
- [`tests/`](/api_htmx/tests): Collection of [unit-tests](https://wikipedia.org/wiki/Unit_testing)
to ensure all functionality defined within the `api_htmx` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
works as expected.
(See [Django's testing documentation](https://docs.djangoproject.com/en/4.2/topics/testing))
- [`templates/ratemymodule/`](/api_htmx/templates/ratemymodule): Contains [HTML](https://wikipedia.org/wiki/HTML)-style
[Django templates](https://docs.djangoproject.com/en/4.2/topics/templates)
that are populated with the necessary [context data](https://docs.djangoproject.com/en/4.2/topics/class-based-views/generic-display#adding-extra-context),
then sent as the final [HTML response](https://docs.djangoproject.com/en/4.2/ref/template-response)
to an [HTMX API](https://htmx.org/docs#ajax) [request](https://docs.djangoproject.com/en/4.2/topics/http)

## REST API

- [`views/`](/api_rest/views): Contains files that in-turn contain collections of [views](https://docs.djangoproject.com/en/4.2/topics/http/views)
to respond to [HTTP requests](https://docs.djangoproject.com/en/4.2/topics/http)
associated with the [REST API](https://wikipedia.org/wiki/REST)
- [`apps.py`](/api_rest/apps.py): Contains the [configuration classes](https://docs.djangoproject.com/en/4.2/ref/applications#application-configuration)
to provide metadata about the `api_rest` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
- [`urls.py/`](/api_rest/urls.py): Contains the list of URLs available to the [REST API](https://wikipedia.org/wiki/REST)
[URL dispatcher](https://docs.djangoproject.com/en/4.2/topics/http/urls)
- [`tests/`](/api_rest/tests): Collection of [unit-tests](https://wikipedia.org/wiki/Unit_testing)
to ensure all functionality defined within the `api_rest` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
works as expected.
(See [Django's testing documentation](https://docs.djangoproject.com/en/4.2/topics/testing))
