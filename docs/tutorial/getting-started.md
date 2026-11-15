# Getting started

From installing the package to seeing the banner on your site and hearing a visitor's choice. You need a Wagtail site.

## Requirements

- Wagtail 7.4, 8.0 or 8.1, with the [Python and Django versions](https://docs.wagtail.org/en/stable/releases/upgrading.html#compatible-django-python-versions) each of them supports
- `wagtail.contrib.settings`, which comes with Wagtail
- `django.template.context_processors.request` in your template settings. Wagtail's project template has it. Without it, the banner doesn't load.

## Install the package and add the banner

1. Install the package:

   ```sh
   pip install wagtail-cookie-consent
   ```

2. Add it to `INSTALLED_APPS`, with `wagtail.contrib.settings`:

   ```python
   INSTALLED_APPS = [
       # ...
       "wagtail.contrib.settings",
       "wagtail_cookie_consent",
       # ...
   ]
   ```

3. Create its table:

   ```sh
   python manage.py migrate
   ```

4. Add the banner to `<head>` in your base template, and the Cookie settings link where you want it, such as the footer:

   ```django
   {% load wagtail_cookie_consent %}
   <!doctype html>
   <html>
     <head>
       <meta charset="utf-8">
       {% cookie_consent %}
       ...
     </head>
     <body>
       ...
       <footer>{% cookie_settings_link %}</footer>
     </body>
   </html>
   ```

5. In the Wagtail admin, go to **Settings → Cookie consent** and choose the categories your site uses.

The banner's scripts and stylesheet are among the package's static files. On a deployed site, run `collectstatic` after you install or upgrade the package, as for any app's static files.

## See the banner

Visit your site in a private window. The banner appears in the corner of the page. Choose **Accept all** or **Necessary only**, and it's gone on the next page; the Cookie settings link in your footer brings the choices back.

Nothing there? See [Troubleshoot](../how-to/troubleshoot.md).

## Hear the choice

Add this before `{% cookie_consent %}` in your base template, then reload and choose again:

```html
<script>
  document.addEventListener("wagtail-cookie-consent:change", (event) => {
    console.log("Cookie choice:", event.detail);
  });
</script>
```

Your browser's console shows the choice, such as `{ analytics: true, marketing: false }`, each time it's made and on each page load after.

## Next

- Make your scripts follow the choice: [Act on the visitor's choice](../how-to/act-on-the-choice.md).
- Match the banner to your site: [Change the colors](../how-to/change-the-colors.md).
- What the banner does and doesn't do: [How the banner works](../explanation/how-the-banner-works.md).
