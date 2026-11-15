# Add the banner to templates outside your base template

A template that doesn't extend your base template, such as a 404 page, needs the banner too:

```django
{% load wagtail_cookie_consent %}
...
{% cookie_consent %}
```
