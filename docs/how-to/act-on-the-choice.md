# Act on the visitor's choice

The package doesn't block or load other scripts for you, and it doesn't delete cookies another script has set. Your own code acts on the choice.

The banner announces the visitor's choice as a `wagtail-cookie-consent:change` event on `document`. Its `detail` has `true` or `false` for each category your site shows:

```js
document.addEventListener("wagtail-cookie-consent:change", (event) => {
  if (event.detail.analytics) {
    // The visitor allows analytics cookies.
  }
});
```

The event is sent when the visitor chooses, when they change their choice, and on each page load once a choice is stored. Before a visitor has chosen, no event is sent.

A stored choice is announced as soon as `{% cookie_consent %}` runs, and again once the banner has loaded. Add your listener before `{% cookie_consent %}` to hear it at the earliest, and make it safe to run more than once.

[wagtail-google-tag](https://github.com/Limitless-Horizons/wagtail-google-tag) listens for this event and updates Google's Consent Mode with it. Put `{% google_tag %}` before `{% cookie_consent %}`.
