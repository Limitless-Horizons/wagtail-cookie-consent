# Script API

## The `wagtail-cookie-consent:change` event

Sent on `document` with the visitor's choice. Its `detail` has `true` or `false` for each category your site shows:

```js
document.addEventListener("wagtail-cookie-consent:change", (event) => {
  event.detail; // { analytics: true, marketing: false }
});
```

It's sent when the visitor chooses, when they change their choice, and on each page load once a choice is stored. Before a visitor has chosen, no event is sent. A stored choice is announced as soon as `{% cookie_consent %}` runs, and again once the banner has loaded.

## `window.wagtailCookieConsent`

There only when the banner is on.

| Member | What it is |
|---|---|
| `categories` | The categories your site shows, such as `["analytics", "marketing"]`. |
| `get()` | The visitor's choice, such as `{ analytics: true, marketing: false }`, or `null` before a choice. |
| `set(choice)` | Stores a choice, as the banner would, and announces it with the `wagtail-cookie-consent:change` event. A category left out is refused. Returns a promise. |
| `hideBanner()` | Closes the banner without a choice, on a page that asks in its own way. |

See [Build your own consent page](../how-to/build-your-own-consent-page.md).

## The cookie

The choice is stored in a cookie named `cc_cookie`, for 182 days. Read the choice through the event or `get()`, not from the cookie.
