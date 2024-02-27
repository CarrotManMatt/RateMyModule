# Django DataBase models & Migrations

## Question What is a model

A [model](https://docs.djangoproject.com/en/5.0/topics/db/models/#module-django.db.models)
is a set of fields making up a table of data, a model maps to a database.
One model has many fields inside it in which data is stored,
fields store a specific data type
E.g. The model “users” could have a field “email” of type “CharField”.

Luckily for us, django manages the database side of things by
automatically turning models into the database type of our choice
and as such we just need to make models, while not worrying too much
about what django is doing in the background to make it work.

### Making a new model

A [new model](https://docs.djangoproject.com/en/5.0/topics/db/models/#quick-example)
is created by importing Models.Model into a class and giving it attributes

``` python
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
```

This Model: Has name "Person" and two fields (attributes) first_name and last_name
which are both CharFields.
Django automatically adds a primary key / ID number to each entry
so we don't need to add it ourselves.

So it is rather simple to make one.

### Using a model

Django needs to be told you want to use the models you have made,
and as such you have to name the module its in settings.py

``` python
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
```

This is what ours looks like,
I believe most have already been put in judging by the commits.

### Doing fields right

Each attribute of the model must be a correctly called
[field](https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.Field)
object. Django won't store normal
attributes like strings or ints in a database.
For RateMyModule Fields should never be null,
just empty strings or equivalent values that represent 'nothing'.
Should you want to set a field to a
different datatype such as for flagging you can use
'[choices](https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.Field.choices)'
to give a set of possible
options for the datatype

### Writing to models

After making your models its time to populate some data.
To
[create](https://docs.djangoproject.com/en/4.2/topics/db/queries/#creating-objects):
an entry make a new instance of the model class,
populate its data in its parameters,
then use `.save()` to add it to the database.

Here is some example code:

```python
from ratemymodule.models import user
u = user(name="Timmy", email="txt@sutdent.bham.ac.uk")
u.save()
```

### Reading from models

To
[get data](https://docs.djangoproject.com/en/4.2/topics/db/queries/#retrieving-objects)
out of our database, We can use `.all()` to get all
records for a given table or use `.filter(<specification>)`
to only get records with a specific feature from a given table.
To do this you need a
[manager](https://docs.djangoproject.com/en/4.2/topics/db/managers/#django.db.models.Manager)
, by default
Django adds a manager called objects to every model class.
But if you want to you can make more managers to better
query the database or just change the name of the manager
if the name 'objects' displeases you.

Such as this sample code:

```python
all_users = User.objects.all()

wild_books = Book.objects.filter(title__contains='wild')
number_wild_books = wild_books.count()
```

## Question So... what is a migration

In simple terms it's best to think of the systems of
migrations as another version control system like Gitlab or Git.
Migrations manage the state of Django's models

A migration is when changes made to models are
packed up into files to describe what has been done,
like git or any other version control system.
Django stores them in “projectdirectory/ratemymodule/migrations”.

So once you have made your models or adapted them,
you need to pack it into an instruction set such that everyone else
and the server knows what it's doing.

### Doing migrations

First start with a
“[makemigrations](https://docs.djangoproject.com/en/3.1/ref/django-admin/#makemigrations)”
command, this turns your changes into instructions that others can use.
This will spit out some migration files,
which can then be applied or edited as you please.

Second,
“[migrate](https://docs.djangoproject.com/en/3.1/ref/django-admin/#migrate)”
to apply those packed changes to the code.

### Specific to RateMyModule

So, due to the choice of the
specific database used by our code “SQLite 3”,
applying certain changes
through migrations can be a bit slow.
SQLite is good in some ways but
it’s more difficult for Django to edit.
Django can manage it but just beware
when you make changes to the structure of a model
(such as number and type of fields) Django
[hacks its way](https://docs.djangoproject.com/en/3.1/topics/migrations/#sqlite)
through by: creating a new table, coping
across all data, dropping old table, renaming the new table.
As our tables shouldn’t be **too** large
this shouldn’t cause much slowdown in running commands but just be aware.

### VCS problems with migrations

Django is sadly not impervious to
[problems](https://docs.djangoproject.com/en/3.1/topics/migrations/#version-control)
with VCS
though, two people could try to merge migrations
with the same ID number or other features causing issues with linearity,
causing a merge conflict. Django can try to
put them in order itself which may cause strange issues,
or you can edit the files yourself. The
files are written in python and assuming you have your IDE set up right
you will get help from PyCharm to make sure
you have edited it right.
Another issue that is common to come across
is dependency, a model can have a foreign key
to another model and as such both
must exist or the Django will get upset.

### Question Made a mistake with migrations

If you have messed up somewhere and need
to undo a migration, you can by
simply running the name of the migration
you want to do (so to backtrack to the last one you were happy with).

## More detail

Here is the
[full link](https://docs.djangoproject.com/en/3.1/topics/migrations/#module-django.db.migrations)
for migrations and
[full link](https://docs.djangoproject.com/en/5.0/topics/db/models/)
for models
to the excellently formatted documentation
I found most helpful when writing this.
link for
[querying](https://docs.djangoproject.com/en/4.2/topics/db/queries/#making-queries)
models/databases

### Please never ever look at the formating hiding behind this file

<3
