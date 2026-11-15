# Add the Cookie settings link

`{% cookie_settings_link %}` renders a button that reopens the visitor's choices. Give it your own label and HTML attributes:

```django
{% cookie_settings_link "Cookies" class="footer-link" %}
```

It has to come from this tag, or carry the same `data-cc="show-preferencesModal"` attribute, so it can't be an ordinary link an editor adds in the CMS. When the banner is off, the tag renders nothing.

The tag's arguments are in the [template tags reference](../reference/template-tags.md).
