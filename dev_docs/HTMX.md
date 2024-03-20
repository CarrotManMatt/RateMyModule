# HTMX
## What is HTMX?
A library that allows you to build dynamic web applications with minimal JavaScript by leveraging HTML attributes.

It aims to enhance user experience by enabling server-side rendering of dynamic content and seamless interaction with the server, all while keeping the codebase simple and maintainable.
## Core Concepts:
### HTML Attributes:
HTMX allows us to leverage HTML attributes in order to build dynamic web applications. To understand how this works, let's take a look at some HTML tags.

The Anchor Tag:
```HTMl
<a href="/blog">Blog</a>
```
    This tells the browser to `GET` `/blog` and display it on the browser
Now, with HTMX in mind, we can consider a different way of performing a similar action with another attribute.
```HTML
<button hx-post="/clicked"
       hx-trigger="click"       hx-target="#parent-div"       hx-swap="outerHTML">
       Click Me!</button>
```
    This will do a couple of things differently to the anchor tag.    It will perform a `HTTP POST` request for `/clicked` where it will `swap` the `outerHTML` of the `parent-div` with contents of the response.This is not possible with default HTML and in this implementation doesn't require a complicated and bloated java script framework to run.

HTMX extends the idea of HTML as hypertext, opening up more possibilities directly within the language
- Any element can issue a HTTP request
- Any event can trigger requests
- Any HTTP verb can be used
- Any element can be the target for update by the request.

>[!info] HTTP Responses:
>When using HTMX, on the server side, you respond with HTML and not JSON.
### DOM Manipulation:
## AJAX Requests:
HTMX allows you to make AJAX requests directly inside of the HTML
### Attributes:
- `hx-get`: Issues a `GET` request
- `hx-post`: Issues a `POST` request
- `hx-put`: Issues a `PUT` request
- `hx-patch`: Issues a `PATCH` request
- `hx-delete`: Issues a `DELETE` request
Each attribute will take a URL to issue an AJAX request to
```html
<div hx-put="/messages">
    Put To Messages</div>
```
### Triggering Requests:
We can set triggers for requests to send within our HTML elements.
the triggers can be set to a range of events using the [`hx-trigger`](https://htmx.org/attributes/hx-trigger/) attribute
```html
<div hx-post="/mouse_entered" hx-trigger="mouseenter">
    [Here Mouse, Mouse!]</div>
```
    Here, the event trigger used is `mouseenter`It is also possible to modify triggers to give more unique behaviour to events for example, let's say we only want the above event to trigger once
```html
<div hx-post="/mouse_entered" hx-trigger="mouseenter once">
    [Here Mouse, Mouse!]</div>
```
Here is a small list of the most useful triggers that you may want to use:
- `changed`: only issues a request if the value of the element has changed.
- `delay:<time interval>`: waits the specified amount of time before issuing a request
- `throttle:<time interval>`: wait the given amount of time before issuing the request, if a new even occurs before the time limit has been reached, the event will be discarded.
- `from:<CSS Selector>`: listen for the event on a different element, used for things like keyboard shortcuts.
**Example:**
```html
<input type="text" name="q"
    hx-get="/trigger_delay"    hx-trigger="keyup changed delay:500ms"    hx-target="#search-results"    placeholder="Search...">
<div id="search-results"></div>
```
    This renders an input field with placeholder text "Search...", it will wait 500ms after a `keyup` event has occured before updating the contents of the div with `id == "search-results`.### Trigger Filters:
HTMX allows you to apply filters to your triggers, this means that the trigger will only run when the given filter evaluates to `true`

An example could be `ctrlKey` which, when applied as a filter on the `click` trigger, will only send the request if the control key is being pressed and the element is clicked
```html
<div hx-get="/clicked" hx-trigger="click[ctrlKey]">
    Control Click Me</div>
```
### Special Events:
There are some extremely useful events given by HTMX that effect the behaviour of `hx-trigger`.

`load` - fires once the element is first loaded
`revealed` - fires only once when an element is first scrolled into the viewport
`intersect` - fires once when an element first intersects the viewport, this supports two additional options:
    `root:<selector>` - a CSS selector of the root element for intersection
    `threshold:<float>` - a floating point number between 0.0 and 1.0, indicating what amount of intersection to fire the event on.
### Polling:
If you want to trigger an action multiple times, you can set up polling to help.
```html
<div hx-get="/news" hx-trigger="every 2s"></div>
```
    This will trigger the event every 2 seconds
Similarly, you can give events a delay such that they trigger after an amount of seconds
```html
<div hx-get="/messages"
     hx-trigger="load delay:1s"     hx-swap="outerHTML" > </div>```
## Features and Functionality *TODO*:
### Dynamic Content Loading:
### Form Submission:
### Client-Side Events:
### Integrations:
### Targets:
Let's say you wanted your response to be loaded into a different element other than the one that is making the request, we can do this by using `hx-target` attribute
```html
<input type="text" name="q"
       hx-get="/trigger_delay"       hx-trigger="keyup delay:500ms changed"       hx-target="#search-results"       placeholder="Search...">
<div id="search-results"></div>
```
    This is going to render the result of the input elememt's trigger into the div with id "search-results"### Extended CSS Selectors:
`hx-target`, and most attributes that take a CSS selector, support an “extended” CSS syntax:

- You can use the `this` keyword, which indicates that the element that the `hx-target` attribute is on is the target
- The `closest <CSS selector>` syntax will find the closest ancestor element or itself, that matches the given CSS selector. (e.g. `closest tr` will target the closest table row to the element)
- The `next <CSS selector>` syntax will find the next element in the DOM matching the given CSS selector.
- The `previous <CSS selector>` syntax will find the previous element in the DOM the given CSS selector.
- `find <CSS selector>` which will find the first child descendant element that matches the given CSS selector. (e.g `find tr` would target the first child descendant row to the element)

In addition, a CSS selector may be wrapped in `<` and `/>` characters, mimicking the query literal syntax of hyperscript.

Relative targets like this can be useful for creating flexible user interfaces without peppering your DOM with loads of `id` attributes.
### Swapping:

### Attribute Inheritance:
## Benefits and Advantages:
### Reduced JavaScript Complexity:
HTMX simplifies front-end development by leveraging HTML attributes for dynamic behaviour, reducing the need for complex JavaScript code.
### Improved Performance:
HTMX improves performance by reducing server load, optimising data transfer and client-side caching.
### Simplified Development:
HTMX simplifies web development by:
- promoting a declarative approach
- minimising JavaScript code
- integrating seamlessly with server-side technologies
- enabling progressive enhancement
- using familiar syntax
- reducing cognitive load
- providing a supportive community and ecosystem for developers.
## Resources and further reading:
- [HTMX documentation](https://htmx.org/docs/)
- [hx-trigger attribute](https://htmx.org/attributes/hx-trigger/)
