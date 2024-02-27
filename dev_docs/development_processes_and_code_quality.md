# Development Processes & Code Quality

## Quick Links

- [Linting](#linting)
- [Type Checking](#type-checking)
- [Django Migration Checking](#django-migration-checking)
- [Docstrings](#docstrings)
- [Comment Mnemonics](#comment-mnemonics)
- [Testing](#testing)
- [Merging Git Branches](#merging-git-branches)

## [Linting](https://wikipedia.org/wiki/Lint_(software))

[Linting](https://wikipedia.org/wiki/Lint_(software)) is the process
of ensuring that all written code adheres to a standardised format.
This makes it easier for every team member to understand, read & maintain the code,
as they are not trying to decipher the [syntactical format of the code](https://wikipedia.org/wiki/Syntax_(programming_languages)),
whilst also trying to understand what it does ([semantics](https://wikipedia.org/wiki/Programming_language#Semantics)).
It is far more important for a team to decide on a consistent format that may be imperfect,
or not preferred by some team members,
rather than each developer using their own preferred format.

RateMyModule uses multiple tools to [lint](https://wikipedia.org/wiki/Lint_(software))
any files committed to the [Git repository](https://phoenixnap.com/kb/what-is-a-git-repository#ftoc-heading-1),
including:

- [ruff](https://ruff.rs) - An extremely fast Python [linter](https://wikipedia.org/wiki/Lint_(software))
  and code formatter, written in [Rust](https://rust-lang.org).
- [pre-commit checks](https://github.com/pre-commit/pre-commit-hooks#hooks-available) -
  Some out-of-the-box hooks for [pre-commit](https://pre-commit.com)
- [PyMarkdown](https://github.com/jackdewinter/pymarkdown) - A [Markdown](https://wikipedia.org/wiki/Markdown)
  [linter](https://wikipedia.org/wiki/Lint_(software))
- [pygrep checks](https://github.com/pre-commit/pygrep-hooks#provided-hooks) -
  A collection of fast, cheap, [regex](https://wikipedia.org/wiki/Regular_expression)-based
  [pre-commit](https://pre-commit.com) hooks.

The more significant tools like [ruff](https://ruff.rs) & [PyMarkdown](https://github.com/jackdewinter/pymarkdown)
have their configuration parameters defined within [the `pyproject.toml` file](/pyproject.toml).
Most of the [pre-commit](https://pre-commit.com) based checks are configured
through the individual arguments provided to each hook (defined within [`.pre-commit-config.yaml`](/.pre-commit-config.yaml)).

<!-- pyml disable-next-line line-length-->
### Some Of Our Project's [Linting](https://wikipedia.org/wiki/Lint_(software)) Rules For Python Code

- Adhere to [PEP8](https://peps.python.org/pep-0008)
- All [imports](https://realpython.com/python-import) must be sorted alphabetically
  & ordered by local/standard library/3rd party
  - Use [ruff's auto import sorting tool](https://docs.astral.sh/ruff/rules#isort-i)
- Use [double quotation marks](https://docs.astral.sh/ruff/settings#format_quote-style)
- Include the [object export declaration](https://geeksforgeeks.org/python-__all__)
  at the top of every Python file ([`__all__`](https://geeksforgeeks.org/python-__all__))
- Use [PascalCase](https://wikipedia.org/wiki/Camel_case#Variations_and_synonyms)
  for all class names
- Use [snake_case](https://wikipedia.org/wiki/Snake_case) for all function & variable names
- Use [ALL_CAPS_CASE](https://wikipedia.org/wiki/All_caps#Computing)
  for [constant immutable variable values](https://realpython.com/python-constants#type-annotating-constants)
- Ensure all [lines are shorter](https://docs.astral.sh/ruff/settings#line-length)
  than 95 characters
  - It is best to split lines using the existing brackets of a calling a function,
    creating a class instance, declaring an iterable, etc.
- Use [f-strings](https://realpython.com/python-f-strings),
  rather than the old-fashioned `.format()` method
- [Compare booleans & `None` with an `is` check, rather than `==`](https://realpython.com/courses/python-is-identity-vs-equality)
- Ensure only explicit exception types are excepted (no [bare excepts](https://docs.astral.sh/ruff/rules/bare-except))
- Use [spaces for indentation](https://docs.astral.sh/ruff/rules/mixed-spaces-and-tabs)
  (not tabs)
- Ensure there is no [whitespace after opening brackets](https://docs.astral.sh/ruff/rules/whitespace-after-open-bracket),
  or [before closing brackets](https://docs.astral.sh/ruff/rules/whitespace-before-close-bracket)
- Ensure there is [whitespace between typed function parameters & default value](https://docs.astral.sh/ruff/rules/missing-whitespace-around-parameter-equals)
- Ensure there is [no whitespace before calling a function](https://docs.astral.sh/ruff/rules/whitespace-before-parameters)
- Ensure there is a [single whitespace between expression operators](https://docs.astral.sh/ruff/rules/missing-whitespace-around-arithmetic-operator)
  (E.g. `x + y`, not `x+y`)
- Ensure there are [no trailing whitespace characters](https://docs.astral.sh/ruff/rules/trailing-whitespace)
  on any line
- Ensure there is a [single new-line character at the end](https://docs.astral.sh/ruff/rules/missing-newline-at-end-of-file)
  of every file
- Use [the `pathlib` package](https://docs.python.org/3/library/pathlib) for file manipulations
  rather than the `os` package functions
  - Always add [full-stops to the end of Exception messages & Docstrings](https://docs.astral.sh/ruff/rules/ends-in-period)
- Every python module should [start with a module-level docstring](https://docs.astral.sh/ruff/rules/undocumented-public-module),
  separated from the code below it by a single blank line

<!-- pyml disable-next-line line-length-->
### Some Of Our Project's [Linting](https://wikipedia.org/wiki/Lint_(software)) [Rules For Markdown Files](https://github.github.com/gfm)

- Use [hashtags (`#`) to define a heading](https://github.github.com/gfm#atx-headings)
- Do not include embedded HTML
- Use [dashes (`-`) for unordered lists](https://github.com/jackdewinter/pymarkdown/blob/main/docs/rules/rule_md004.md)
  (like this list)
- Ensure there are [no trailing whitespace characters](https://github.com/jackdewinter/pymarkdown/blob/main/docs/rules/rule_md009.md)
  on any line
- Ensure there is a [single new-line character at the end](https://github.com/jackdewinter/pymarkdown/blob/main/docs/rules/rule_md047.md)
  of every file
- Ensure all [lines are shorter than 95 characters](https://github.com/jackdewinter/pymarkdown/blob/main/docs/rules/rule_md013.md)
- Use [backticks to define a multi-line code block](https://github.com/jackdewinter/pymarkdown/blob/main/docs/rules/rule_md046.md)
- Ensure every [multi-line code block declares the language](https://github.github.com/gfm#info-string)
  of the code written within it

## Type Checking

Python uses [duck typing](https://wikipedia.org/wiki/Duck_typing):
if it has the ability for an operation to be run upon it, it will succeed,
otherwise an [exception will be raised](https://realpython.com/python-exceptions).
This means that the actual concrete type of an object is never known
(especially when the structure of an object can be dramatically changed at run-time).
However, there are static type checking tools that are run over your code,
that can interpret the types of objects
and provide errors if invalid operations would be performed on an object.
This naturally constrains the typing system of Python
as objects should not have their structure edited at run-time.

This project uses the [static type checker](https://wikipedia.org/wiki/Type_system#Static_type_checking)
called [mypy](https://mypy-lang.org).
[mypy](https://mypy-lang.org) relies upon [type annotations](https://realpython.com/python-type-checking#annotations)
(sometimes known as type hints) to correctly infer/interpret the required type of an object.

Here is an example of a type-annotated function:

```python
def foo(bar: str, baz: int) -> int:
  print(bar)
  return baz + 1
```

### Using Explicit Type Annotations

When writing code, it is important to be as explicit as possible
with the required type annotations,
so that [mypy](https://mypy-lang.org) can notify you of as many errors,
that may occur, as possible.

For example, it is better to write:

```python
my_baz: Baz
i: int
for i in range(5, 10):
  e: ValueError
  try:
    foo(i, "bar")
  except ValueError as e:
    inner: str
    outer: str
    inner, outer = foo(i, "bar")[0:2]
    print(outer)
    my_baz = Baz(inner)
  else:
    my_baz = Baz("baz")
```

rather than:

```python
for i in range(5, 10):
  val: float = bongo(i)
  try:
    foo(i, "bar", float)
  except ValueError as e:
    inner, outer = foo(i, "bar", float)[0:2]
    print(outer)
    my_baz = Baz(inner)
  else:
    my_baz = Baz("baz")
```

It is a common misconception that [type annotations](https://realpython.com/python-type-checking#annotations)
can only be used with variable assignment, or function parameter declarations.
[Type annotations](https://realpython.com/python-type-checking#annotations)
should be used whenever a new variable is being declared.

### Collection Types

Many types within Python inherit from a group called [collection types](https://realpython.com/python-collections-module)
(E.g. `dict`, `list`, `tuple`, `set`, `str`).
These all include differing operations from one another, and also some common ones.
When annotating the type of a variable as a collection object,
it is essential that you are only as restrictive as the operations
to be performed on the object.

For example, if you are only going to iterate (loop) over a given object,
you should allow any [`Iterable` object](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)
to be passed in, rather than explicitly requiring a [list](https://realpython.com/python-list):

```python
from collections.abc import Iterable

def foo(bar: Iterable[str]) -> int:
  value: int = 0

  baz: str
  for baz in bar:
    if baz.endswith("foo"):
      value += 1

  return value
```

What if I want to pass in a [tuple](https://realpython.com/python-tuple)!?
Your function would perform fine,but your [type annotations](https://realpython.com/python-type-checking#annotations)
prevent me.
**Don't** do this:

```python
def foo(bar: list[str]) -> int:
  value: int = 0

  baz: str
  for baz in bar:
    if baz.endswith("foo"):
      value += 1

  return value
```

### Don't use `Any`, use `object`

There may be cases when the type of an object is not known.
In this case it may seem natural to use the `Any` type,
as this suppresses type-checkers when looking at this value.
However, this is the incorrect way to annotate the type of this object
because it allows *every* operation to be performed upon it,
whereas it is not known if *any* operation can be performed upon it.
Instead, [the correct type annotation to use is the `object` type](https://mypy.readthedocs.io/en/stable/dynamic_typing.html#any-vs-object),
which **cannot** have any operation performed upon it
and must be passed through an [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance)/[`hasattr()`](https://docs.python.org/3/library/functions.html#hasattr)
check before an operation can be performed.
Being explicit with saying that the object's type is unknown improves type-safety.

### Overriding Object Methods

When using [the Django framework](https://www.djangoproject.com/),
it is incredibly common for developers to write classes
that [inherit from a longer chain of parent classes](https://realpython.com/inheritance-composition-python#the-object-super-class).
This naturally means that many (if not most) of the methods being written,
within that [child class](https://realpython.com/inheritance-composition-python#whats-inheritance),
will be overriding methods from the parent class.
To ensure a consistent method structure between the parent & child classes,
a function decorator called [`@override`](https://typing.readthedocs.io/en/latest/spec/class-compat.html#override)
is essential to be used.
This prevents incompatible function structures
and allows the [docstring](https://realpython.com/documenting-python-code#documenting-your-python-code-base-using-docstrings)
to be inherited from the [parent class](https://realpython.com/inheritance-composition-python#the-object-super-class).

For example:

```python
from typing import override

class Bar(Foo):
  @override
  def calculate_baz(self, x: int, y: int) -> float:
    baz: float = super().calculate_baz(x=x, y=y)

    if baz > 11.9:
      print("FooBar!")

    return baz
```

#### Calling Super Methods With Arguments

When calling a [superclasses](https://realpython.com/inheritance-composition-python#the-object-super-class)
method (here `super().baz()`),
it is essential that you pass every argument as a [keyword argument](https://w3schools.com/python/gloss_python_function_keyword_arguments.asp)
(rather than as a [positional argument](https://geeksforgeeks.org/keyword-and-positional-argument-in-python)),
so that if the function structure/argument order ever changes,
you will not encounter silent argument ordering errors.
Be explicit!

For example:

```python
super().calculate_baz(x=x, y=y)
```

rather than:

```python
super().calculatebaz(x, y)
```

### Incompatibilities

There are some places, within python code,
that [type annotations](https://realpython.com/python-type-checking#annotations)
are not syntactically possible to provide.
Some examples are [lambda function](https://realpython.com/python-lambda#python-lambda-and-regular-functions)
definitions & [list/set/generator/dictionary comprehensions](https://geeksforgeeks.org/comprehensions-in-python).
The suggestion for this project in these cases is to:

- Not use [lambda functions](https://realpython.com/python-lambda#python-lambda-and-regular-functions)
  - Define a new fully formed function with [type annotations](https://realpython.com/python-type-checking#annotations)
- Continue to use [comprehensions](https://geeksforgeeks.org/comprehensions-in-python)
  - Allow [mypy](https://mypy-lang.org)'s type inference
    to guess the types within comprehensions

### Encountering Errors

When the [static type checker](https://wikipedia.org/wiki/Type_system#Static_type_checking)
is run over your code, it may produce an obscenely large number of errors.
This is because this project's [mypy configuration](https://mypy.readthedocs.io/en/stable/config_file.html)
(defined within [the `pyproject.toml` file](/pyproject.toml)) sets it to run in strict mode.
Strict mode means more errors are caught, and thus, once they are fixed,
it will make the code more type safe.
Adding code to this repository will never require it to pass static type checking,
due to that being a significant burden upon other developers of the project.
Instead, there are more confident developers that will make changes to your submitted code,
to adhere to the type-checking rules.

It is essential that developers within this project leave a type-checking error as failing
(for another developer to fix), rather than suppressing it with a `# type: ignore` flag,
if the developer does not feel confident in fixing the issue.

## Django Migration Checking

Before code can be committed (even locally),
a [pre-commit](https://pre-commit.com/) check will run to ensure that the Python code,
declaring the [Django model definitions](https://docs.djangoproject.com/en/4.2/topics/db/models),
is consistent with the created migrations.
That is, if new changes have been made to the Django models,
but have not been reflected in the migrations,
an error will occur that will prevent the code from being committed.
This also prevents committing broken models code,
because making the migrations naturally requires valid code.

If this error occurs, the simplest fix is to run the `manage.py` command: `makemigrations`.

## Docstrings

Docstrings provide essential in-file documentation,
correctly linked to the necessary Python entities.
Ruff (the static code linter) will show errors if docstrings are not provided,
or if they are incorrectly formatted.
Putting docstrings within the code allows other developers to understand the purpose
of the given class/function without needing to refer to external documentation.

It is always preferable to include any class-wide/function-wide notes
inside that class/function's docstring rather than as in-line comment.
This is because many developers skip over reading comments,
and they can often be lost when code is transmitted between presentation/viewing tools.

## Comment Mnemonics

When comments are used within code,
they should have their purpose explicitly marked by a mnemonic.
In-line comments should be in the format: `<code>··#·<mnemonic>:·<comment>`
(E.g. `print("Hello")  # TODO: Change to output username`)
The list of acceptable comment mnemonics is [here](https://peps.python.org/pep-0350#mnemonics).
Docstrings and type hinting is preferred over using the NOTE mnemonic in a comment
(see [the section above on Docstrings](#docstrings)).

## Correct Import Style

- Never import individual functions/variables from another package/module
  - Always import the whole package/module so that the global namespace does not get diluted
  - E.g. `from django.contrib import admin` (using `admin.site` later on),
    not `from django.contrib.admin import site`
- If there is a high likelihood that modules with similar names
  will be imported from multiple packages,
  the imports should use the higher level package name
  - E.g. `import core` (using `core.urls.utils` later on)
    and `import django` (using `django.urls.utils` later on)
- If the necessary module is not importable from the parent package,
  an alias that includes the parent package's name can be used
  - E.g. `from core.urls import utils as core_url_utils`
    and `from django import urls as django_urls`
- Classes should be imported individually from modules/packages
  - E.g. `from typing import Final`, not `import typing` (using `typing.Final` later on)

## Testing

The `tests/` directory of every app within this project contains the complete test suite,
to unit-test every part of that given app.
All tests should be limited in scope to ensure they have no variability due to side effects.
Running the tests is done automatically during the CI/CD pipeline,
but it can be beneficial to also run them manually to ensure local changes to the codebase
adhere to the required functionality of the project.

## Merging Git Branches

Each Git branch should contain a single "unit" of work that can be wholly merged
back into the main branch without containing invalid code/missing references.
This is not to say that every merge request must contain a fully functional feature,
but should **never** prevent the successful running of the server in the merged state.
