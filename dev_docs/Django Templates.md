# Django Templates
## What is a Django template?
A template is Django’s way of rendering static parts of the desired HTML output.

This includes a special syntax for describing how dynamic content will be inserted.
## Configuring templates:
Multiple template engines exist for Django out of the box,
these include its own template system called **Django Templating Language (DTL)** as well as a popular alternative called **Jina2**.

It's not a requirement to have a template engine and additionally, you can use a third-party engine or write your own template backend.

A standard API exists, provided by Django, to render templates regardless of the backend.

RateMyModule makes use of the default Django Templating Language, Here is a comprehensive guide to DTL so that the developers of RateMyModule can create effective and high quality templates for the application.

>[!caution] Warning!
> **The template system isn’t safe against untrusted authors.**
> - A site **must never** allow users to provide their own templates
> - These template authors can perform attacks and access properties that may contain sensitive information.
## Django Templating Language:
Before we move on to seeing `base.html` and `home.html`, we need to understand what the syntax we will see actually means.
### Variables:
- Outputs a value from the context, a dict-like object
```Django
My first name is {{ first_name }}. My last name is {{ last_name }}.
```
- given the context:
```python
{
 'first_name': 'John', 'last_name': 'Doe'}
```
- would result in:
```django
My first name is John. My last name is Doe.
```

### Tags:
- Tags provide logic in the rendering process
- They can:
    - Output content
    - serve as a control structure e.g. `if` statements and `for` loops
    - Grab content from the database
    - Enable access to other tags
- tags are encased by `{%%}`
```Django
# Basic tag
{% csrf_token %}

# Tag with arguments
{% cycle 'odd' 'even' %}

# Tag requires ending tags
{% if user.is_authenticated %}
    Hello, {{ user.username }}.{% endif %}
```

### Filters
- Filters transform the value of variable and tag arguments
- So given `{'django: 'the web framework for perfectionists with deadlines'}`
```django
{{ django|title }}
```
- would render to
```django
The Web Framework For Perfectionists With Deadlines
```

### Comments
- comments are not rendered
- a single line comment looks like:
```django
{# This is a comment #}
```
- a multi line comment looks like:
```django
{% comment %}
this is comment line 1
this is comment line 2
{% endcomment %}
```

### Blocks
- These are slightly more complicated and define sections of code that can be inherited and overridden between templates
**Basic Syntax:**
```django
{% block name %}
    ...{% endblock %}
```
### Inheritance:
- Let's say we have a template called `base.html`, in this file we have HTML that describes how every webpage should look
```django
<!DOCTYPE html>
<html lang="en">
<head>
    <title>RateMyModule</title></head>
<body>
    <div id='userInfo' name='userInfo'>        {% block userInfo %}        {% endblock %}    </div></body>
</html>
```
- In here we have a block called `userInfo`
- Now, we've determined we want every webpage to have `userInfo` but it won't render anything unless we override it.
- We are going to override it inside of `home.html`
```django
{% extends "base.html" %}

{% block userInfo %}
{% for user in UserList %}
<h2>
    {{ user.get_name }}</h2>
{% endfor %}
{% endblock %}
```
- Now when `home.html` is rendered, it will inherit all of `base.html` and override the `userInfo` block with it's own logic.
### Static Files:
- It's very common that a web application such as RateMyModule would want to serve static files to the user
- A static file could be an image, JavaScript file or CSS file.
- In order to enable this functionality, you must make sure that `django.contrib.staticfiles` is included inside `INSTALLED_APPS`
- Also in the settings file, define `STATIC_URL`
```python
STATIC_URL = "static/"
```
**Loading a static file inside a template:**
- we are going to make use of the `static` template tag:
```django
{% load static %}
<img src="{% static 'my_app/example.jpg' %}" alt="My image">
```
**Storing static files:**
- Ensure that static files are stored inside a directory called `static` inside your application

## Context Data:
- Django templates allow us to pass in context data to allow rendering of dynamic HTML as well as content from the database.
- Here I will demonstrate how we can render context data into `home.html`
### urls.py
- first of all we need to look in our applications `urls.py` file and create an endpoint that will render `home.html`
```python
from django.urls import path

from . import views

urlpatterns = [
   path("", views.home, name="home")
]
```
- This creates the endpoint that display's the `home` view which will render our template
### views.py
- Now we need to create a view to render our template.
- This file can be called `views.py` or similarly be called `__init__.py` given it is in the apps `views` directory
```python
from django.shortcuts import render
from django.http import HttpResponse
from .models import User_List

def home(response):
    return render(response, "../templates/home.html", {"UserList": User_List})
```
### Result
Now, when a user goes to the correct URL i.e. the default application URL, `home.html` will render with the correct `UserList` inside of it.
## Forms in Templates:
When we want the user to input some data, we need to create what is called a `form` inside our template.

we need to start by creating our form in `forms.py`
```python
from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label="Your name", max_length=100)
```
Now we can create a method in our `views.py` file to render the form inside `name.html`
```python
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import NameForm


def get_name(request):

    if request.method == "POST":
        form = NameForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect("/thanks/")
    else:        form = NameForm()
    return render(request, "name.html", {"form": form})
```
Finally, we need to display our form inside `name.html`
```django
<form action="/your-name/" method="post">
    # a tag implemented to avoid malicious attacks    {% csrf_token %}    {{ form }}    <input type="submit" value="Submit"></form>
```

>[!caution] Important
>The _{% csrf_token %}_ tag is significant in Django for form handling. It generates a hidden input field containing a CSRF token, which is required for secure form submissions.
## Best Practices:
1. **Decide on templating engine**
    - Django has a default template although you can use 3rd party templates, change template in `settings.py`
2. **Keep templates consistent**
    - Django makes assumptions about the structure of your project when it's looking for templates, it searches for the `/templates` directory but this can be changed
3. **Use template inheritance**
    - It's important to take advantage of Django's inheritance system. You should have templates such as `base.html` which have child templates, inheriting blocks from the parent.
4. **Be mindful of handling querysets**
    - Handling queries can significantly impact performance due to the tight coupling with Django's ORM layer. This can lead to excessive database queries causing slowdowns or crashes. To optimise, using Django mechanisms like `select_related` or `prefetch_related` is crucial. For instance, replacing `User.objects.all()` with `User.objects.select_related('profile')` reduces queries by including related profile instances. For complex relationships like many-to-many or one-to-many, `prefetch_related` is preferred.
5. **Keep templates simple and concise**
    - Avoid writing complex logic inside templates, it's better to write complex logic inside views or models. This ensures your templates are clean and maintainable. Additionally, you should use comments to document your code `{% comment %}`
6. **Avoid hardcoding URLs and string by using URL namespaces**
    - Avoid hardcoding URLs and strings by leveraging URL namespaces in Django. Use the `{% url %}` tag to dynamically generate URLs based on view names or URL patterns, and employ Django’s translation framework for string translations. Incorporating namespaces simplifies template development by ensuring unique URL names, even across different applications. This prevents naming conflicts and allows for concise URL references within templates, enhancing readability and manageability.
7. **Consider template caching**
    - Template caching is a valuable method for speeding up rendering of templates, you can reduce server load and improve performance by frequently caching regularly used pre-populated templates.
## Resources and Further Reading:
- Simple introduction to templates in Django:
    - [Django Tutorial - Templates & Custom HTML | Tech With Tim](https://www.youtube.com/watch?v=b0CgA_Ap_Mc)
    - [Related Blog Post](https://www.techwithtim.net/tutorials/django/html-templates)
- Django Templates Documentation
    - [Django Template Language](https://docs.djangoproject.com/en/5.0/ref/templates/language/#top)
    - [Connecting Templates, Views and Models](https://docs.djangoproject.com/en/5.0/intro/tutorial03/)
- Django Template Best Practices
    - [Django Templates: Best practices for web development | CodiumAI Team](https://www.codium.ai/blog/django-templates-best-practices-for-web-development/)
