# Running The Development Server Locally

## Quick Links

- [Creating A PyCharm Run Configuration](#creating-a-pycharm-run-configuration)
- [Setting Environment Variables](#setting-environment-variables)
- [Manually Running The Development Server From The Terminal](#manually-running-the-development-server-from-the-terminal)

## Creating A PyCharm Run Configuration

One of the features that makes developing with [Django in PyCharm](https://jetbrains.com/help/pycharm/django-support7.html)
easier is [saved run-configurations](https://jetbrains.com/help/pycharm/run-debug-configuration.html).
These are stored commands with extra instructions that describe how to run the code
in this project during [development](https://codecademy.com/article/environments#heading-local-development-environment).
The instructions below show you how to set up your own [run-configuration](https://jetbrains.com/help/pycharm/run-debug-configuration-django-server.html)
for [a local instance of the Django development server](https://jetbrains.com/help/pycharm/run-debug-configuration-django-server.html):

1. Select [the run-configurations drop-down in the top-right of any main UI page in PyCharm](https://jetbrains.com/help/pycharm/run-debug-configurations-dialog.html).
(It is likely to be showing the default [run-configuration](https://jetbrains.com/help/pycharm/run-debug-configuration.html)
`Current File`)
2. Select `Edit Configurations` from the drop-down list
3. Click the `+` (plus) icon in the top-left of [the pop-up settings screen](https://jetbrains.com/help/pycharm/2023.3/run-debug-configurations-dialog.html)
to add a new [run-configuration](https://jetbrains.com/help/pycharm/run-debug-configuration.html)
4. Select [`Django Server`](https://jetbrains.com/help/pycharm/run-debug-configuration-django-server.html)
from the available [run-configuration templates list](https://jetbrains.com/help/pycharm/run-debug-configuration.html#templates)
5. Give your newly created [run-configuration](https://jetbrains.com/help/pycharm/run-debug-configuration-django-server.html)
a suitable name.
(E.g. `Run Local Django Development Server`)
6. Under [`Modify options`](https://jetbrains.com/help/pycharm/run-debug-configuration-django-server.html)
select `Run browser` to open a [web-page](https://wikipedia.org/wiki/Web_page)
to your [locally running server](https://docs.djangoproject.com/en/4.2/intro/tutorial01#the-development-server)
every time you run this [run-configuration](https://jetbrains.com/help/pycharm/run-debug-configuration-django-server.html)
7. Click the `Apply` button in the bottom-right corner of [the pop-up](https://jetbrains.com/help/pycharm/2023.3/run-debug-configurations-dialog.html)
to save your changes
8. You can now close [the pop-up](https://jetbrains.com/help/pycharm/2023.3/run-debug-configurations-dialog.html)
9. Your newly created [run-configuration](https://jetbrains.com/help/pycharm/run-debug-configuration-django-server.html)
can be run by clicking [the big green play (`▷`) button](https://jetbrains.com/help/pycharm/run-tool-window.html)
in the top-right of any main UI page.

## Setting Environment Variables

When running the [development server](https://docs.djangoproject.com/en/4.2/intro/tutorial01#the-development-server),
there are some required [environment variables](https://wikipedia.org/wiki/Environment_variable)
that you will need to set.
Most of the required [environment variables](https://wikipedia.org/wiki/Environment_variable)
are [secret values](https://delinea.com/what-is/application-secrets)
that [*must not* be committed to the remote repository](https://littlemaninmyhead.wordpress.com/2021/04/05/why-we-shouldnt-commit-secrets-into-source-code-repositories).
The easiest way to set these values is to follow the steps below:

1. Copy the [`.env.example`](/.env.example) file to a new file called [`.env`](https://blog.bitsrc.io/a-gentle-introduction-to-env-files-9ad424cc5ff4)
in [the root of the project](/../..)
2. Edit this new [`.env` file](https://blog.bitsrc.io/a-gentle-introduction-to-env-files-9ad424cc5ff4)
to remove any of the [environment variables](https://wikipedia.org/wiki/Environment_variable)
that are not marked as `!!!REQUIRED!!!`
3. Generate a new value for the [`SECRET_KEY` environment variable](https://docs.djangoproject.com/en/4.2/ref/settings#secret-key)
using [this online key-gen tool (Djecrety)](https://djecrety.ir)
4. Add the defined values for all the OAUTH [environment variables](https://wikipedia.org/wiki/Environment_variable).
Someone in your team is likely to have already set up the [external OAUTH providers](https://docs.allauth.org/en/latest/socialaccount/providers),
so **check with your team as to where the existing values for these environment variables
are stored!**
5. Set the [environment variable](https://wikipedia.org/wiki/Environment_variable) `PRODUCTION` to `False`
6. When [`DEBUG`](https://docs.djangoproject.com/en/4.2/ref/settings#debug) is set to `True`
any [emails](https://docs.djangoproject.com/en/4.2/topics/email)
(E.g. [email address verification messages](https://docs.allauth.org/en/latest/account/views.html#email-verification))
will be sent to the console,
this means that you **don't** need to set any of [the `EMAIL_` environment variables](https://docs.djangoproject.com/en/4.2/topics/email#smtp-backend)

## Manually Running The Development Server From The Terminal

[The saved run-configurations tool](https://jetbrains.com/help/pycharm/run-debug-configuration.html)
provided by [PyCharm](https://jetbrains.com/pycharm) *should* be sufficient for you to run
[the Django development server](https://docs.djangoproject.com/en/4.2/intro/tutorial01#the-development-server)
locally.
If, however, you find the need to run [the local Django development server](https://docs.djangoproject.com/en/4.2/intro/tutorial01#the-development-server)
from your [terminal](https://wikipedia.org/wiki/Terminal_emulator),
you can use the below [command](https://wikipedia.org/wiki/Command-line_interface#Anatomy_of_a_shell_CLI):

```shell
poetry run python manage.py runserver localhost:8000
```

You can then view the running [web pages](https://wikipedia.org/wiki/Web_page) from the [URL](https://wikipedia.org/wiki/URL):
http://localhost:8000
