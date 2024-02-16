# Setting Up Pycharm

## 1. Install [PyCharm Professional](https://jetbrains.com/pycharm)

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

## 2. Setup Git

1. Install [Git](https://git-scm.com) for your desired OS
2. Configure your [OS-dependent line separators](https://wikipedia.org/wiki/Newline#Representation)
with the following commands:

### On [Windows](https://wikipedia.org/wiki/Microsoft_Windows)

```shell
git config --global core.autocrlf true
```

### On [Linux](https://wikipedia.org/wiki/Linux)

```shell
git config --global core.autocrlf input
```

## 3. Install [Python 3.12](https://python.org/downloads/release/python-3122)

This project requires [Python 3.12](https://python.org/downloads/release/python-3122)
specifically.
You have to use this version, even if you already have a lower version (E.g. Python 3.11)
already installed.

If you already have [Python 3.12](https://python.org/downloads/release/python-3122) installed,
you can skip this step.

### Installing [Python 3.12](https://python.org/downloads/release/python-3122) on [Windows](https://wikipedia.org/wiki/Microsoft_Windows)

The [Windows](https://wikipedia.org/wiki/Microsoft_Windows) installer can be downloaded [here](https://python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe).

### Installing [Python 3.12](https://python.org/downloads/release/python-3122) on [Linux](https://wikipedia.org/wiki/Linux)

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
you will need to install [Python 3.12](https://python.org/downloads/release/python-3122)
from source.
Make sure that you install [Python 3.12](https://python.org/downloads/release/python-3122)
under a different alias, so that it does not conflict with your pre-installed Python version
(E.g. `python312` instead of ~~`python3`~~).
A good set of installation instructions can be found [here](https://aruljohn.com/blog/install-python#download-python-3122-source).

## 4. Install [Poetry](https://python-poetry.org)

[Poetry](https://python-poetry.org) is the [dependency management system](https://python-poetry.org/docs/managing-dependencies)
this project uses.
Install it using the official installer (**not ~~pipx~~**);
the official installation instructions can be found [here](https://python-poetry.org/docs#installing-with-the-official-installer).
**Make sure you follow these instructions EXACTLY**,
because many issues can occur if you do not read the installation instructions correctly.

## 5. Create a Local Version of this Repository

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
## 6. Set Up a [Python Interpreter](https://jetbrains.com/help/pycharm/configuring-python-interpreter.html) & Install [Dependencies](https://python-poetry.org/docs/managing-dependencies) Using [Poetry](https://python-poetry.org)

1. Open the settings pop-up (`Ctrl+Alt+S`),
then navigate to the `Project: {project name} > Python Interpreter` page
2. Click `Add Interpreter`, then choose `🏠 Add Local Interpreter...`
3. Because you have already installed [Poetry]([Poetry](https://python-poetry.org))
you should see the `Poetry Environment` option, select this
4. Choose `New Poetry Environment` (**not ~~`Existing environment`~~**)
5. Select [Python 3.12](https://python.org/downloads/release/python-3122)
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

## 7. Set Up Django within your Pycharm Workspace

1. Open [Pycharm's settings pop-up](https://jetbrains.com/help/pycharm/settings-preferences-dialog.html)
(`Ctrl+Alt+S`),
then navigate to the [`Languages & Frameworks > Django` page](https://jetbrains.com/help/pycharm/django-support.html)
2. Check [`Enable Django Support`](https://jetbrains.com/help/pycharm/django-support.html#b67b4fb4)
3. Select the directory you started this project in as [`Django project root:`](https://jetbrains.com/help/pycharm/django-support.html#b67b4fb4)
4. Select the file `core/settings.py` in the [`Settings:` input box](https://jetbrains.com/help/pycharm/django-support.html#b67b4fb4)
5. Click the `Apply` button in the bottom-right corner to save your changes
6. Navigate to the [`Project: {project name} > Project Structure` settings page](https://jetbrains.com/help/pycharm/project-structure-dialog.html)
7. Mark the following directories as [`Sources`](https://jetbrains.com/help/pycharm/project-structure-dialog.html#dc5370fc):
`api_htmx/`, `api_rest/`, `core/`, `ratemymodule/` & `web/`
8. Mark the following directories as [`Tests`](https://jetbrains.com/help/pycharm/project-structure-dialog.html#dc5370fc):
`api_htmx/tests/`, `api_rest/tests/`, `ratemymodule/tests/` & `web/tests/`
9. Mark the following directories as [`Templates`](https://jetbrains.com/help/pycharm/project-structure-dialog.html#dc5370fc):
`api_htmx/templates/` & `web/templates/`
10. Click the `Apply` button in the bottom-right corner to save your changes
