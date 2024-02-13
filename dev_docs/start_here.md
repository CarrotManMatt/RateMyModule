# Start Here

## Quick Links

- [Getting Started](#getting-started)
- [Running The Development Server Locally](running_the_development_server_locally.md)
- [Git Commit Messages](#git-commit-messages)
- [Adding New Django Aspects](adding_new_django_aspects.md)
- [Licence](#licence)
- [Project Structure](project_structure.md)
- [Setting Up Pycharm](setting_up_pycharm.md)

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
to start developing this project, are found in the [Setting Up Pycharm section](setting_up_pycharm.md).

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

## Licence

Please note that any contributions you make will be made under the terms of the
[GNU General-Public Licence V3](/LICENSE).
