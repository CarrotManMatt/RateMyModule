# Developing

## Quick Links

- [Getting Started](#getting-started)
- [Git Commit Messages](#git-commit-messages)
- [License](#license)
- [Project Structure](#project-structure)
- [Setting Up Pycharm](#setting-up-pycharm)

## Getting Started

Developing RateMyModule is based around [Git](https://git-scm.com) as a [version control system](https://wikipedia.org/wiki/Version_control).
Although this means that any changes are accepted into this repository
from any valid [Git push](https://git-scm.com/docs/git-push),
it is recommended to complete your local development using the [PyCharm Professional IDE](https://jetbrains.com/pycharm)
(**not ~~Pycharm Community Edition~~**).
This is because [PyCharm Professional](https://jetbrains.com/pycharm) includes
[many helpful features](https://jetbrains.com/help/pycharm/django-support7.html#django-support)
for developing with [Django](https://djangoproject.com).
Full instructions on setting up, from scratch, your [PyCharm Professional IDE](https://jetbrains.com/pycharm),
to start developing this project, are found in the [Setting Up Pycharm section](#setting-up-pycharm).

## Git Commit Messages

Commit messages should be written in the imperative present tense. For example, "Fix bug #1".
Commit subjects should start with a capital letter and **not** end in a full-stop.

Additionally, you should keep the commit subject under 80 characters
for a comfortable viewing experience on GitLab and other git tools.
If you need more space for your message, please use the body of the commit.
(See [Robert Painsi's Commit Message Guidelines](https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53)
for how to write good commit messages.)

For example:

```none
Prevent users from being able to delete our database

<more detailed description here>
```

## License

Please note that any contributions you make will be made under the terms of the
[GNU General Public License V3](LICENSE).

## Project Structure

### Top Level Files

- [`manage.py`](manage.py): Runs as a command-line utility to perform administrative tasks.
(See [the Django documentation about `manage.py`](https://docs.djangoproject.com/en/4.2/ref/django-admin))
- [`pyproject.toml`](pyproject.toml): Orchestrates project metadata & dependencies.
(See [Poetry's documentation](https://python-poetry.org/docs/pyproject))
- [`.env.example`](.env.example): List of every environment variable setting
that can be configured when deploying this project.
This file can be renamed to `.env` in deployment (along with changing the necessary settings),
to enable customisation of the deployment settings

### Top-Level Python Packages

Each top-level Python package is configured as a [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications).
Every top-level Python package will have an `__init__.py` file
containing the standard [`__all__` declaration](https://stackoverflow.com/a/64130/14403974).
However, this [`__all__` declaration](https://stackoverflow.com/a/64130/14403974)
should be empty, as Django apps should not export any objects directly.

- [`core`](core): The core [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
that includes the configuration for the [project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)'s
webserver as a whole
- [`ratemymodule`](ratemymodule): The primary [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
that defines the database models & request independent [CRUD](https://codecademy.com/article/what-is-crud)
actions
- [`web`](web): The main HTML web server [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
that encompasses how to respond to [web requests](https://docs.djangoproject.com/en/4.2/topics/http)
sent to this [Django project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
- [`api_htmx`](api_htmx): The [HTMX](https://htmx.org) API [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
that defines how to respond to [HTMX](https://htmx.org) [AJAX](https://wikipedia.org/wiki/Ajax_(programming))
[requests](https://docs.djangoproject.com/en/4.2/topics/http) from web-based users
- [`api_rest`](api_rest): The [REST](https://wikipedia.org/wiki/REST) API [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
that defines how to respond to [JSON](https://json.org) [API](https://wikipedia.org/wiki/API)
[requests](https://docs.djangoproject.com/en/4.2/topics/http) from [third-party API](https://wikipedia.org/wiki/Open_API)
users

### Core

- [`settings.py`](core/settings.py): Contains the all configurations
for the entirety of this [Django project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications).
(See [Django's settings documentation](https://docs.djangoproject.com/en/4.2/topics/settings))
- [`urls.py`](core/urls.py): The core [URL dispatcher](https://docs.djangoproject.com/en/4.2/topics/http/urls)
entry point, which defines how to traverse to every other [app's individual URL dispatcher](https://docs.djangoproject.com/en/4.2/topics/http/urls#including-other-urlconfs).
(See [Django's URL dispatcher documentation](https://docs.djangoproject.com/en/4.2/topics/http/urls))
- [`utils.py`](core/utils.py): Contains common utility functions & classes,
used within the `core` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications).
These must all be [lazily loaded](https://docs.djangoproject.com/en/4.2/topics/performance/#understanding-laziness)
because they are imported before any of the [Django apps](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
have been set up.
(I.e. **Do not import any objects from any of the [Django apps](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)**)
- [`views.py`](core/views.py): Contains any simplistic [views](https://docs.djangoproject.com/en/4.2/topics/http/views)
used directly within [`core/urls.py`](core/urls.py)
- [`wsgi.py`](core/wsgi.py): Defines how WSGI webservers can process incoming [web requests](https://docs.djangoproject.com/en/4.2/topics/http)
with this [Django project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications).
This has been automatically generated and is unlikely to need to be changed

### RateMyModule

- [`models/__init__.py`](ratemymodule/models/__init__.py):
Holds the definition for every [DB model](https://docs.djangoproject.com/en/4.2/topics/db/models)
used in this [Django project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications),
alongside any request independent [CRUD](https://codecademy.com/article/what-is-crud) actions,
relating to each [model](https://docs.djangoproject.com/en/4.2/topics/db/models)
- [`models/utils.py`](ratemymodule/models/utils.py):
Contains common utility functions & classes used by the definition of [models](https://docs.djangoproject.com/en/4.2/topics/db/models)
within [`models/__init__.py`](ratemymodule/models/__init__.py)
- [`admin/__init__.py`](ratemymodule/admin/__init__.py): Defines how to display the [models](https://docs.djangoproject.com/en/4.2/topics/db/models),
inside this [Django project](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications),
on the [automatic admin UI](https://docs.djangoproject.com/en/4.2/ref/contrib/admin) pages
- [`migrations/`](ratemymodule/migrations): Contains auto-generated [database migrations](https://docs.djangoproject.com/en/4.2/topics/migrations)
([one migration per file](https://docs.djangoproject.com/en/4.2/topics/migrations#migration-files)).
These are used by [Django's database engine](https://docs.djangoproject.com/en/4.2/ref/databases)
to ensure that the database matches the model definitions
specified within [`models/__init__.py`](ratemymodule/models/__init__.py)
- [`tests/`](ratemymodule/tests): Collection of [unit-tests](https://wikipedia.org/wiki/Unit_testing)
to ensure all functionality defined within the `ratemymodule` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
works as expected.
(See [Django's testing documentation](https://docs.djangoproject.com/en/4.2/topics/testing))
- [`apps.py`](ratemymodule/apps.py): Contains the [configuration classes](https://docs.djangoproject.com/en/4.2/ref/applications#application-configuration)
to provide metadata about the `ratemymodule` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)

### Web

- [`views/`](web/views): Contains files that in-turn contain collections of [views](https://docs.djangoproject.com/en/4.2/topics/http/views)
to respond to [HTTP requests](https://docs.djangoproject.com/en/4.2/topics/http)
associated with the primary web request responder
- [`apps.py`](web/apps.py): Contains the [configuration classes](https://docs.djangoproject.com/en/4.2/ref/applications#application-configuration)
to provide metadata about the `web` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
- [`urls.py/`](web/urls.py): Contains the list of URLs available to the primary web server
[URL dispatcher](https://docs.djangoproject.com/en/4.2/topics/http/urls)
- [`tests/`](web/tests): Collection of [unit-tests](https://wikipedia.org/wiki/Unit_testing)
to ensure all functionality defined within the `web` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
works as expected.
(See [Django's testing documentation](https://docs.djangoproject.com/en/4.2/topics/testing))
- [`templates/ratemymodule/`](web/templates/ratemymodule): Contains [HTML](https://wikipedia.org/wiki/HTML)-style
[Django templates](https://docs.djangoproject.com/en/4.2/topics/templates)
that are populated with the necessary [context data](https://docs.djangoproject.com/en/4.2/topics/class-based-views/generic-display#adding-extra-context),
then sent as the final [HTML response](https://docs.djangoproject.com/en/4.2/ref/template-response)
to an [HTTP web request](https://docs.djangoproject.com/en/4.2/topics/http)
- [`static/ratemymodule/`](web/static/ratemymodule): Contains all [static files](https://docs.djangoproject.com/en/5.0/howto/static-files)
that are served alongside [HTML](https://docs.djangoproject.com/en/4.2/ref/template-response)
[web requests]((https://docs.djangoproject.com/en/4.2/topics/http)).
(E.g. image, [CSS](https://wikipedia.org/wiki/CSS) & [JS](https://wikipedia.org/wiki/JavaScript)
files)

### HTMX API

- [`views/`](api_htmx/views): Contains files that in-turn contain collections of [views](https://docs.djangoproject.com/en/4.2/topics/http/views)
to respond to [HTTP requests](https://docs.djangoproject.com/en/4.2/topics/http)
associated with the [HTMX API](https://htmx.org/docs#ajax)
- [`apps.py`](api_htmx/apps.py): Contains the [configuration classes](https://docs.djangoproject.com/en/4.2/ref/applications#application-configuration)
to provide metadata about the `api_htmx` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
- [`urls.py/`](api_htmx/urls.py): Contains the list of URLs available to the HTMX API [URL dispatcher](https://docs.djangoproject.com/en/4.2/topics/http/urls)
- [`tests/`](api_htmx/tests): Collection of [unit-tests](https://wikipedia.org/wiki/Unit_testing)
to ensure all functionality defined within the `api_htmx` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
works as expected.
(See [Django's testing documentation](https://docs.djangoproject.com/en/4.2/topics/testing))
- [`templates/ratemymodule/`](api_htmx/templates/ratemymodule): Contains [HTML](https://wikipedia.org/wiki/HTML)-style
[Django templates](https://docs.djangoproject.com/en/4.2/topics/templates)
that are populated with the necessary [context data](https://docs.djangoproject.com/en/4.2/topics/class-based-views/generic-display#adding-extra-context),
then sent as the final [HTML response](https://docs.djangoproject.com/en/4.2/ref/template-response)
to an [HTMX API](https://htmx.org/docs#ajax) [request](https://docs.djangoproject.com/en/4.2/topics/http)

### REST API

- [`views/`](api_rest/views): Contains files that in-turn contain collections of [views](https://docs.djangoproject.com/en/4.2/topics/http/views)
to respond to [HTTP requests](https://docs.djangoproject.com/en/4.2/topics/http)
associated with the [REST API](https://wikipedia.org/wiki/REST)
- [`apps.py`](api_rest/apps.py): Contains the [configuration classes](https://docs.djangoproject.com/en/4.2/ref/applications#application-configuration)
to provide metadata about the `api_rest` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
- [`urls.py/`](api_rest/urls.py): Contains the list of URLs available to the [REST API](https://wikipedia.org/wiki/REST)
[URL dispatcher](https://docs.djangoproject.com/en/4.2/topics/http/urls)
- [`tests/`](api_rest/tests): Collection of [unit-tests](https://wikipedia.org/wiki/Unit_testing)
to ensure all functionality defined within the `api_rest` [Django app](https://docs.djangoproject.com/en/4.2/ref/applications#projects-and-applications)
works as expected.
(See [Django's testing documentation](https://docs.djangoproject.com/en/4.2/topics/testing))

## Setting Up Pycharm

### 1. Install [PyCharm Professional](https://jetbrains.com/pycharm)

Although [PyCharm Professional](https://jetbrains.com/pycharm)
is an *extremely* expensive subscription-based IDE,
the great news is that as students we get free access!
[GitHub's Student Developer Pack](https://education.github.com/pack) gives you access
to [PyCharm Professional](https://jetbrains.com/pycharm)
for every year that you are at university!

Once you have signed up for [GitHub's Student Developer Pack](https://education.github.com/pack),
you can go to [the JetBrains account connection page](https://jetbrains.com/student/?authMethod=github),
to connect your [GitHub](https://github.com/account) account to your [JetBrains account](https://account.jetbrains.com)
(create one if necessary).

Now you can download & install [PyCharm Professional](https://jetbrains.com/pycharm/download)
for your chosen operating system.

### 2. Setup Git

1. Install [Git](https://git-scm.com) for your desired OS
2. Configure your [OS-dependent line separators](https://wikipedia.org/wiki/Newline#Representation)
with the following commands:

#### On [Windows](https://wikipedia.org/wiki/Microsoft_Windows):

```shell
git config --global core.autocrlf true
```

#### On [Linux](https://wikipedia.org/wiki/Linux):

```shell
git config --global core.autocrlf input
```

### 3. Install [Python 3.12](https://python.org/downloads/release/python-3121)

This project requires [Python 3.12](https://python.org/downloads/release/python-3121)
specifically.
You have to use this version, even if you already have a lower version (E.g. Python 3.11),
already installed.

If you already have [Python 3.12](https://python.org/downloads/release/python-3121) installed,
you can skip this step.

#### Installing [Python 3.12](https://python.org/downloads/release/python-3121) on [Windows](https://wikipedia.org/wiki/Microsoft_Windows)

The [Windows](https://wikipedia.org/wiki/Microsoft_Windows) installer can be downloaded [here](https://python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe).

#### Installing [Python 3.12](https://python.org/downloads/release/python-3121) on [Linux](https://wikipedia.org/wiki/Linux)

If you are running an [Ubuntu](https://ubuntu.com)-based [distribution](https://wikipedia.org/wiki/Linux_distribution)
you can add the [deadsnakes third-party repository](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa),
that contains [updated versions of Python](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa/+packages)
(including [3.12](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa/+packages#pub15420947-expander)).
Instructions for installing [Python 3.12](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa/+packages#pub15420947-expander)
from the [deadsnakes repository](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa)
can be found [here](https://makeuseof.com/install-python-ubuntu#use-deadsnakes-ppa-to-install-python-3-12-on-ubuntu).

If you are running an [Arch Linux](https://archlinux.org)-based [distribution](https://wikipedia.org/wiki/Linux_distribution)
you can install [Python 3.12](https://aur.archlinux.org/packages/python312) from the [AUR](https://wiki.archlinux.org/title/AUR).

In all other [Linux distributions](https://wikipedia.org/wiki/Linux_distribution)
you will need to install [Python 3.12](https://python.org/downloads/release/python-3121)
from source.
Make sure that you install [Python 3.12](https://python.org/downloads/release/python-3121)
under a different alias, so that it does not conflict with your pre-installed Python version
(E.g. `python312` instead of ~~`python3`~~).
A good set of installation instructions can be found [here](https://aruljohn.com/blog/install-python#download-python-3121-source).

### 4. Install [Poetry](https://python-poetry.org)

[Poetry](https://python-poetry.org) is the [dependency management system](https://python-poetry.org/docs/managing-dependencies)
this project uses.
Install it using the official installer (**not ~~pipx~~**);
the official installation instructions can be found [here](https://python-poetry.org/docs#installing-with-the-official-installer).
**Make sure you follow these instructions EXACTLY**,
because many issues can occur if you do not read the installation instructions correctly.

### 5. Create a Local Version of this Repository

1. Open Pycharm, then close any currently open projects
2. Ensure you have the [GitLab plugin](https://plugins.jetbrains.com/plugin/22857-gitlab)
installed.
This comes pre-bundled with [PyCharm](https://jetbrains.com/pycharm)
& can be installed from the [`Plugins` page](https://plugins.jetbrains.com/pycharm)
3. Return to the `Projects` page, then click `Get from VCS`
4. Choose [GitLab](https://plugins.jetbrains.com/plugin/22857-gitlab) as your VCS provider
5. Connect [PyCharm](https://jetbrains.com/pycharm) to your [UoB CS GitLab Account](https://git.cs.bham.ac.uk/-/profile)
by [generating a token](https://git.cs.bham.ac.uk/-/user_settings/personal_access_tokens),
then entering it into the input box (the default selected API permissions are suitable)
6. Select `Team Projects 2023-24 / RateMyModule` from the list of projects,
then choose a suitable directory for your local version of the repository to be saved to
7. Wait for [PyCharm](https://jetbrains.com/pycharm) to finish indexing your new project

<!-- pyml disable-next-line line-length-->
### 6. Set Up a [Python Interpreter](https://jetbrains.com/help/pycharm/configuring-python-interpreter.html) & Install [Dependencies](https://python-poetry.org/docs/managing-dependencies) Using [Poetry](https://python-poetry.org)

1. Open the settings pop-up (`Ctrl+Alt+S`),
then navigate to the `Project: {project name} > Python Interpreter` page
2. Click `Add Interpreter`, then choose `🏠 Add Local Interpreter...`
3. Because you have already installed [Poetry]([Poetry](https://python-poetry.org))
you should see the `Poetry Environment` option, select this
4. Choose `New Poetry Environment` (**not ~~`Existing environment`~~**)
5. Select [Python 3.12](https://python.org/downloads/release/python-3121)
from the `Base interpreter:` drop-down menu
6. **Uncheck** `Install packages from pyproject.toml`
7. Click `OK` to create the new [Python virtual environment](https://realpython.com/python-virtual-environments-a-primer#what-is-a-python-virtual-environment)
8. Open a new [terminal pane](https://jetbrains.com/help/pycharm/terminal-emulator.html)
(`Alt+F12`) and run the below commands to install all the necessary dependencies:

```shell
poetry install --no-root --sync
```

```shell
poetry run pre-commit install
```

### 7. Set Up Django within your Pycharm Workspace

1. Open [Pycharm's settings pop-up](https://jetbrains.com/help/pycharm/settings-preferences-dialog.html)
(`Ctrl+Alt+S`),
then navigate to the [`Languages & Frameworks > Django` page](https://jetbrains.com/help/pycharm/django-support.html)
2. Check [`Enable Django Support`](https://jetbrains.com/help/pycharm/django-support.html#b67b4fb4)
3. Select the directory you started this project in as [`Django project root:`](https://jetbrains.com/help/pycharm/django-support.html#b67b4fb4)
4. Select the file `core/settings.py` in the [`Settings:` input box](https://jetbrains.com/help/pycharm/django-support.html#b67b4fb4)
5. Click the `Apply` button in the bottom-right corner to save your changes
6. Navigate to the [`Project: {project name} > Project Structure` settings page](https://jetbrains.com/help/pycharm/project-structure-dialog.html)
7. Mark the following directories as [`Sources`](https://jetbrains.com/help/pycharm/project-structure-dialog.html#dc5370fc):
`api_htmx/`, `api_rest/`, core/`, `ratemymodule/` & `web/`
8. Mark the following directories as [`Tests`](https://jetbrains.com/help/pycharm/project-structure-dialog.html#dc5370fc):
`api_htmx/tests/`, `api_rest/tests/`, `ratemymodule/tests/` & `web/tests/`
9. Mark the following directories as [`Templates`](https://jetbrains.com/help/pycharm/project-structure-dialog.html#dc5370fc):
`api_htmx/templates/` & `web/templates/`
10. Click the `Apply` button in the bottom-right corner to save your changes
