/**
 * Wagtail cookie consent: runs the vanilla-cookieconsent banner with the
 * site's settings, and announces the visitor's choice as a
 * "wagtail-cookie-consent:change" event on document. The event's detail has
 * one true or false value for each category the site shows, for example
 * { analytics: true, marketing: false }.
 *
 * The choice is announced when the visitor makes or changes it, and on each
 * page load once one is stored. A stored choice is announced as soon as this
 * script runs, before the banner library has loaded, so that scripts waiting
 * for it (such as an analytics tag) hear it early.
 */
(() => {
  const configElement = document.getElementById(
    'wagtail-cookie-consent-config',
  );
  if (!configElement || configElement.dataset.started) return;
  configElement.dataset.started = 'true';

  const config = JSON.parse(configElement.textContent);
  const text = config.text;

  // The banner library's own cookie.
  const COOKIE_NAME = 'cc_cookie';

  const announce = (accepted) => {
    const detail = {};
    config.categories.forEach((category) => {
      detail[category] = accepted.includes(category);
    });
    document.dispatchEvent(
      new CustomEvent('wagtail-cookie-consent:change', { detail }),
    );
  };

  /**
   * The categories in a stored choice, or null when there's none. A choice
   * made under another revision (the site has since changed the categories it
   * shows) doesn't count: the banner asks again.
   */
  const storedCategories = () => {
    const match = document.cookie.match(
      new RegExp(`(?:^|;\\s*)${COOKIE_NAME}=([^;]+)`),
    );
    if (!match) return null;
    try {
      const stored = JSON.parse(decodeURIComponent(match[1]));
      return stored.consentId &&
        stored.revision === config.revision &&
        Array.isArray(stored.categories)
        ? stored.categories
        : null;
    } catch {
      return null;
    }
  };

  const stored = storedCategories();
  if (stored) announce(stored);

  // The banner library puts its text in the page as HTML.
  const escape = (value) =>
    String(value).replace(
      /[&<>"']/g,
      (character) =>
        ({
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#39;',
        })[character],
    );

  const privacyLink = config.privacy
    ? `<a href="${escape(config.privacy.url)}">${escape(config.privacy.label)}</a>`
    : '';

  const categories = { necessary: { enabled: true, readOnly: true } };
  const sections = [
    {
      description: [escape(text.description), privacyLink]
        .filter(Boolean)
        .join(' '),
    },
    {
      title: escape(text.necessaryTitle),
      description: escape(text.necessaryText),
      linkedCategory: 'necessary',
    },
  ];
  config.categories.forEach((category) => {
    categories[category] = {};
    sections.push({
      title: escape(text[`${category}Title`]),
      description: escape(text[`${category}Text`]),
      linkedCategory: category,
    });
  });

  const run = () => {
    if (!window.CookieConsent) return;
    window.CookieConsent.run({
      hideFromBots: config.hideFromBots,
      revision: config.revision,
      categories,
      onConsent: ({ cookie }) => announce(cookie.categories),
      onChange: ({ cookie }) => announce(cookie.categories),
      language: {
        default: 'en',
        translations: {
          en: {
            consentModal: {
              title: escape(text.title),
              description: escape(text.description),
              acceptAllBtn: escape(text.acceptAll),
              acceptNecessaryBtn: escape(text.necessaryOnly),
              showPreferencesBtn: escape(text.customize),
              footer: privacyLink,
            },
            preferencesModal: {
              title: escape(text.settingsTitle),
              acceptAllBtn: escape(text.acceptAll),
              acceptNecessaryBtn: escape(text.necessaryOnly),
              savePreferencesBtn: escape(text.save),
              closeIconLabel: escape(text.close),
              sections,
            },
          },
        },
      },
    });
  };

  // The library's script is deferred, so it's there by DOMContentLoaded.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
