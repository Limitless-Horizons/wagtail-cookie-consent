# Template tags

```django
{% load wagtail_cookie_consent %}
```

Both tags need the request in the template context (`django.template.context_processors.request`).

## `{% cookie_consent %}`

The banner, with its scripts and stylesheet. Put it in `<head>`, once per page. It takes no arguments.

It renders nothing when the banner is off: “Show the banner to” is “No one”, no category is checked, or the page is a Wagtail preview.

## `{% cookie_settings_link %}`

A button that reopens the visitor's choices.

```django
{% cookie_settings_link %}
{% cookie_settings_link "Cookies" class="footer-link" %}
```

| Argument | Default | What it does |
|---|---|---|
| The label, as the first argument | “Cookie settings” | The button's text. |
| Any keyword argument | None | Becomes an HTML attribute on the button, such as `class`. |

It renders `<button type="button" data-cc="show-preferencesModal">`, and nothing when the banner is off.
