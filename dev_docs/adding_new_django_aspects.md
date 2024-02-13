# Adding New Django Aspects

## Quick Links

- [Adding A New DB Model](#adding-a-new-db-model)
- [Adding A Model To The Admin UI](#adding-a-model-to-the-admin-ui)
- [Adding A New Web URL](#adding-a-new-web-url)
- [Adding A New HTMX API URL](#adding-a-new-htmx-api-url)
- [Adding A New Web View](#adding-a-new-web-view)
- [Adding A New HTMX API View](#adding-a-new-htmx-api-view)
- [Adding A New Web HTML Template](#adding-a-new-web-html-template)
- [Adding A New HTMX API HTML Template](#adding-a-new-htmx-api-html-template)
- [Adding Static Files](#adding-static-files)

## Adding A New DB [Model](https://docs.djangoproject.com/en/4.2/topics/db/models)

- Add your [model class](https://docs.djangoproject.com/en/4.2/topics/db/models)
inside [`ratemymodule/models/__init__.py`](/ratemymodule/models/__init__.py)
- Make sure your [model class](https://docs.djangoproject.com/en/4.2/topics/db/models) [inherits](https://docs.djangoproject.com/en/4.2/topics/db/models#model-inheritance)
from `CustomBaseClass` (found within [`models/utils.py`](/ratemymodule/models/utils.py))
- If you [override the super-class'](https://geeksforgeeks.org/method-overriding-in-python)
[`clean()`](https://docs.djangoproject.com/en/4.2/ref/models/instances#django.db.models.Model.clean)
or [`save()`](https://docs.djangoproject.com/en/4.2/ref/models/instances#django.db.models.Model.save)
methods make sure you [call back to the superclass](https://realpython.com/python-super)
using `super().clean()` or `super().save(*args, **kwargs)`, respectively.
(See [Django's documentation on overriding model methods](https://docs.djangoproject.com/en/4.2/topics/db/models#overriding-model-methods))
- Make sure every [field in your model](https://docs.djangoproject.com/en/4.2/topics/db/models#fields)
has a [translatable string](https://docs.djangoproject.com/en/4.2/topics/i18n/translation#lazy-translations)
for [the `verbose_name` for that field](https://docs.djangoproject.com/en/4.2/ref/models/fields#verbose-name).
(See the existing `User` model as an example)
- Make sure you add a [translatable](https://docs.djangoproject.com/en/4.2/topics/i18n/translation#lazy-translations)
[`verbose_name`](https://docs.djangoproject.com/en/4.2/ref/models/options#verbose-name)
to [the `class Meta:` of your model](https://docs.djangoproject.com/en/4.2/topics/db/models#meta-options).
(See the existing `User` model as an example)
- Read-only shortcut accessors can be defined with [the `@property` decorator](https://realpython.com/python-property)
- Any [model fields](https://docs.djangoproject.com/en/4.2/topics/db/models#fields)
should **not** be [type-annotated](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html).
(E.g. `first_name = models.CharField(max_length=50)`,
not ~~`first_name: str = models.CharField(max_length=50)`~~)
- After finishing your [model class](https://docs.djangoproject.com/en/4.2/topics/db/models),
**before committing your changes**, run these [`manage.py` commands](https://docs.djangoproject.com/en/4.2/ref/django-admin)
to [migrate your Python changes to the database](https://docs.djangoproject.com/en/4.2/topics/migrations):

```shell
makemigrations
```

```shell
migrate
```

(You can run these commands easily within [PyCharm's `manage.py` interface](https://jetbrains.com/help/pycharm/running-manage-py.html#run).
Open it using the shortcut `Ctrl+Alt+R`)

## Adding A Model To The Admin UI

- Add your new [admin-configuration class](https://docs.djangoproject.com/en/4.2/ref/contrib/admin#modeladmin-objects)
inside [`ratemymodule/admin/__init__.py`](/ratemymodule/admin/__init__.py)
- Use [the `@admin.display()` decorator](https://docs.djangoproject.com/en/4.2/ref/contrib/admin#the-display-decorator)
to make a calculation function into something that can be displayed within [the admin interface](https://docs.djangoproject.com/en/4.2/ref/contrib/admin).
(See the [`UserAdmin`](/ratemymodule/admin/__init__.py) class as an example)

## Adding A New Web [URL](https://wikipedia.org/wiki/URL)

- Add your new [URL](https://wikipedia.org/wiki/URL) inside [the `view_urlpatterns` list](https://docs.djangoproject.com/en/4.2/topics/http/urls#syntax-of-the-urlpatterns-variable),
within [`web/urls.py`](/web/urls.py)
- Your [URL](https://wikipedia.org/wiki/URL)
must [**not** start with a leading-forward-slash (`/`)](https://docs.djangoproject.com/en/4.2/topics/http/urls#example)
- Your [URL](https://wikipedia.org/wiki/URL) must [end with a trailing-forward-slash (`/`)](https://docs.djangoproject.com/en/4.2/topics/http/urls#example)
- [The `route` string parameter](https://docs.djangoproject.com/en/4.2/ref/urls#django.urls.path)
to [the `django.urls.path()` function](https://docs.djangoproject.com/en/4.2/ref/urls#django.urls.path)
must be [a raw string](https://realpython.com/python-raw-strings).
(See the existing [URL patterns](https://docs.djangoproject.com/en/4.2/topics/http/urls#syntax-of-the-urlpatterns-variable)
within [`web/urls.py`](/web/urls.py) for examples)
- Your [URL pattern](https://docs.djangoproject.com/en/4.2/ref/urls#django.urls.path)
should be named, so that it can be [reverse referenced](https://docs.djangoproject.com/en/4.2/ref/urlresolvers#reverse)
throughout this project.
(See [Django's documentation on naming URL patterns](https://docs.djangoproject.com/en/4.2/topics/http/urls#naming-url-patterns)
for more information on why this is beneficial)
- Use the full expansion of the import location of [the `path()` function (`django.urls.path()`)](https://docs.djangoproject.com/en/4.2/ref/urls#django.urls.path)
to make it clear which `path()` function is being used

## Adding A New HTMX API [URL](https://wikipedia.org/wiki/URL)

- Add your new [URL](https://wikipedia.org/wiki/URL) inside [the `urlpatterns` list](https://docs.djangoproject.com/en/4.2/topics/http/urls#syntax-of-the-urlpatterns-variable),
within [`api_htmx/urls.py`](/api_htmx/urls.py)
- Your [URL](https://wikipedia.org/wiki/URL)
must [**not** start with a leading-forward-slash (`/`)](https://docs.djangoproject.com/en/4.2/topics/http/urls#example)
- Your [URL](https://wikipedia.org/wiki/URL) must [end with a trailing-forward-slash (`/`)](https://docs.djangoproject.com/en/4.2/topics/http/urls#example)
- [The `route` string parameter](https://docs.djangoproject.com/en/4.2/ref/urls#django.urls.path)
to [the `django.urls.path()` function](https://docs.djangoproject.com/en/4.2/ref/urls#django.urls.path)
must be [a raw string](https://realpython.com/python-raw-strings).
(See the existing [URL patterns](https://docs.djangoproject.com/en/4.2/topics/http/urls#syntax-of-the-urlpatterns-variable)
within [`api_htmx/urls.py`](/api_htmx/urls.py) for examples)
- Your [URL pattern](https://docs.djangoproject.com/en/4.2/ref/urls#django.urls.path)
should be named, so that it can be [reverse referenced](https://docs.djangoproject.com/en/4.2/ref/urlresolvers#reverse)
throughout this project.
(See [Django's documentation on naming URL patterns](https://docs.djangoproject.com/en/4.2/topics/http/urls#naming-url-patterns)
for more information on why this is beneficial)
- Use the full expansion of the import location of [the `path()` function (`django.urls.path()`)](https://docs.djangoproject.com/en/4.2/ref/urls#django.urls.path)
to make it clear which `path()` function is being used

## Adding A New Web [View](https://docs.djangoproject.com/en/4.2/topics/http/views)

- Add your [view](https://docs.djangoproject.com/en/4.2/topics/http/views)
 inside [`web/views/__init__.py`](/web/views/__init__.py)
- Use a [class-based-view](https://docs.djangoproject.com/en/4.2/topics/class-based-views)
that inherits at least from [the base `View`](https://docs.djangoproject.com/en/4.2/ref/class-based-views/base#django.views.generic.base.View)
- Name your view using [PascalCase](https://wikipedia.org/wiki/Camel_case#Variations_and_synonyms).
(E.g. `HomeView`)
- Your view must end with the word `View`. (E.g. `HomeView`)
- Any configuration [class-variables](https://realpython.com/python-classes#class-attributes)
should **not** be [type-annotated](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html).
(E.g. `template_name = "ratemymodule/home.html"`,
not ~~`template_name: str = "ratemymodule/home.html"`~~)

## Adding A New HTMX API [View](https://docs.djangoproject.com/en/4.2/topics/http/views)

- Add your [view](https://docs.djangoproject.com/en/4.2/topics/http/views)
inside [`api_htmx/views/__init__.py`](/api_htmx/views/__init__.py)
- Use a [class-based-view](https://docs.djangoproject.com/en/4.2/topics/class-based-views)
that inherits at least from [the base `View`](https://docs.djangoproject.com/en/4.2/ref/class-based-views/base#django.views.generic.base.View)
- Name your view using [PascalCase](https://wikipedia.org/wiki/Camel_case#Variations_and_synonyms).
(E.g. `LoginPopUpView`)
- Your view must end with the word `View`. (E.g. `LoginPopUpView`)
- Any configuration [class-variables](https://realpython.com/python-classes#class-attributes)
should **not** be [type-annotated](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html).
(E.g. `template_name = "ratemymodule/htmx_fragments/login_pop_up.html"`,
not ~~`template_name: str = "ratemymodule/htmx_fragments/login_pop_up.html"`~~)

## Adding A New Web [HTML Template](https://docs.djangoproject.com/en/4.2/topics/templates)

- Add your new [HTML template](https://docs.djangoproject.com/en/4.2/topics/templates)
inside [`web/templates/ratemymodule/](/web/templates/ratemymodule)
- Make sure your [template](https://docs.djangoproject.com/en/4.2/topics/templates)
[extends](https://docs.djangoproject.com/en/4.2/ref/templates/language#template-inheritance)
from [`web/templates/ratemymodule/base.html`](/web/templates/ratemymodule/base.html)
by adding this [template-tag](https://docs.djangoproject.com/en/4.2/topics/templates#tags)
to the top of your [HTML template](https://docs.djangoproject.com/en/4.2/topics/templates):
[`{% extends "ratemymodule/base.html" %}`](https://docs.djangoproject.com/en/4.2/ref/templates/builtins#extends).
([Extending](https://docs.djangoproject.com/en/4.2/ref/templates/language#template-inheritance)
from [`web/templates/ratemymodule/base.html`](/web/templates/ratemymodule/base.html)
ensures your [HTML template](https://docs.djangoproject.com/en/4.2/topics/templates)
contains consistent styling, favicons, the header & the footer,
as defined in [the base HTML template](/web/templates/ratemymodule/base.html))
- Add the [`{% load static %}`](https://docs.djangoproject.com/en/4.2/ref/templates/builtins#load)
[template-tag](https://docs.djangoproject.com/en/4.2/topics/templates#tags)
to the top of your [HTML template](https://docs.djangoproject.com/en/4.2/topics/templates)
to [enable](https://docs.djangoproject.com/en/4.2/ref/templates/builtins#load)
[referencing the location of static files](https://docs.djangoproject.com/en/4.2/ref/templates/builtins#static).
(E.g. when [locating the source of an image](https://docs.djangoproject.com/en/4.2/ref/templates/builtins#std-templatetag-static))

## Adding A New HTMX API [HTML Template](https://docs.djangoproject.com/en/4.2/topics/templates)

- Add your new [HTML template](https://docs.djangoproject.com/en/4.2/topics/templates) fragment
inside [`api_htmx/templates/ratemymodule/htmx_fragments/](/api_htmx/templates/ratemymodule/htmx_fragments)
- Make sure your [template](https://docs.djangoproject.com/en/4.2/topics/templates)
**does not** [extend](https://docs.djangoproject.com/en/4.2/ref/templates/language#template-inheritance)
from a wider [HTML template](https://docs.djangoproject.com/en/4.2/topics/templates)
within [`web/templates/ratemymodule/`](/web/templates/ratemymodule).
([HTML template](https://docs.djangoproject.com/en/4.2/topics/templates) fragments
are [delivered to HTMX on the client device](https://htmx.org/docs#ajax)
and [placed within existing major HTML templates that have already been served to the client](https://htmx.org/docs#swapping))
- Add the [`{% load static %}`](https://docs.djangoproject.com/en/4.2/ref/templates/builtins#load)
[template-tag](https://docs.djangoproject.com/en/4.2/topics/templates#tags)
to the top of your [HTML template](https://docs.djangoproject.com/en/4.2/topics/templates)
to [enable](https://docs.djangoproject.com/en/4.2/ref/templates/builtins#load)
[referencing the location of static files](https://docs.djangoproject.com/en/4.2/ref/templates/builtins#static).
(E.g. when [locating the source of an image](https://docs.djangoproject.com/en/4.2/ref/templates/builtins#std-templatetag-static))

## Adding [Static Files](https://mattlayman.com/understand-django/serving-static-files#what-are-static-files)

- Store [static files](https://mattlayman.com/understand-django/serving-static-files#what-are-static-files)
(E.g. [images](https://wikipedia.org/wiki/Digital_image))
within the [`web/static/ratemymodule/`](/web/static/ratemymodule) [directory](https://wikipedia.org/wiki/Directory_(computing))
- It may be useful to organise files into [subdirectories](https://merriam-webster.com/dictionary/subdirectory)
within [`web/static/ratemymodule/`](/web/static/ratemymodule).
(E.g. [`web/static/ratemymodule/favicon/`](/web/static/ratemymodule/favicon)
contains all files relating to [favicon](https://wikipedia.org/wiki/Favicon)s)
