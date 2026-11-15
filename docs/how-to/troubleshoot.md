# Troubleshoot

- **No banner on the page:** “Show the banner to” is “No one”, no category is checked, the page is a preview, or `collectstatic` hasn't run. Run `python manage.py check` too: it warns when the request isn't in the template context.
- **No banner, though it's on:** you've already chosen. Use the Cookie settings link, or delete the `cc_cookie` cookie.
- **No banner in browser tests:** see [Automated browsers](see-the-banner-in-browser-tests.md).
