import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { JSDOM } from 'jsdom';

const SCRIPT = readFileSync(
  new URL(
    '../../src/wagtail_cookie_consent/static/wagtail_cookie_consent/js/cookie-consent.js',
    import.meta.url,
  ),
  'utf8',
);

const TEXT = {
  title: 'We use cookies',
  description: 'Some cookies are needed.',
  acceptAll: 'Accept all',
  necessaryOnly: 'Necessary only',
  customize: 'Customize',
  settingsTitle: 'Cookie settings',
  save: 'Save my choices',
  close: 'Close',
  necessaryTitle: 'Necessary',
  necessaryText: 'Always on.',
  analyticsTitle: 'Analytics',
  analyticsText: 'Counts visits.',
  marketingTitle: 'Marketing',
  marketingText: 'Videos and ads.',
};

const CONFIG = {
  categories: ['analytics', 'marketing'],
  revision: 3,
  text: TEXT,
  privacy: null,
  hideFromBots: true,
};

const stored = (categories, revision = 3) =>
  `cc_cookie=${encodeURIComponent(
    JSON.stringify({ consentId: 'abc', categories, revision }),
  )}`;

/**
 * A page with the banner's config, with the script run. The banner library is
 * a stand-in that records the options it's run with. `library: 'late'` adds it
 * only after the script has run, as a deferred script would be.
 */
function page(config, { cookie, library = 'early' } = {}) {
  // As Django's json_script writes it, with "<" escaped.
  const json = JSON.stringify(config).replaceAll('<', '\\u003C');
  const head = config
    ? `<script id="wagtail-cookie-consent-config" type="application/json">${json}</script>`
    : '';
  const dom = new JSDOM(
    `<!doctype html><html><head>${head}</head><body></body></html>`,
    { runScripts: 'outside-only', url: 'https://example.com/' },
  );
  const { window } = dom;
  if (cookie) window.document.cookie = cookie;

  window.announced = [];
  window.document.addEventListener('wagtail-cookie-consent:change', (event) => {
    window.announced.push(JSON.parse(JSON.stringify(event.detail)));
  });

  const addLibrary = () => {
    window.runs = [];
    window.CookieConsent = { run: (options) => window.runs.push(options) };
  };
  if (library === 'early') addLibrary();
  window.eval(SCRIPT);
  if (library === 'late') {
    window.announcedBeforeLibrary = [...window.announced];
    addLibrary();
  }
  // The script waits for this when the page is still loading.
  window.document.dispatchEvent(new window.Event('DOMContentLoaded'));
  return window;
}

const english = (window) => window.runs[0].language.translations.en;

test('without the config, nothing runs', () => {
  const window = page(null);
  assert.deepEqual(window.runs, []);
  assert.deepEqual(window.announced, []);
});

test('the banner library runs once, with the site settings', () => {
  const window = page(CONFIG);
  window.eval(SCRIPT);
  assert.equal(window.runs.length, 1);
  const options = window.runs[0];
  assert.equal(options.hideFromBots, true);
  assert.equal(options.revision, 3);
  assert.deepEqual(JSON.parse(JSON.stringify(options.categories)), {
    necessary: { enabled: true, readOnly: true },
    analytics: {},
    marketing: {},
  });
});

test('hideFromBots follows the setting', () => {
  const window = page({ ...CONFIG, hideFromBots: false });
  assert.equal(window.runs[0].hideFromBots, false);
});

test('only the categories a site shows are offered', () => {
  const window = page({ ...CONFIG, categories: ['analytics'] });
  assert.deepEqual(
    [...Object.keys(window.runs[0].categories)],
    ['necessary', 'analytics'],
  );
  const linked = english(window)
    .preferencesModal.sections.map((section) => section.linkedCategory)
    .filter(Boolean);
  assert.deepEqual([...linked], ['necessary', 'analytics']);
});

test('nothing is announced before a visitor has chosen', () => {
  const window = page(CONFIG);
  assert.deepEqual(window.announced, []);
});

test('a stored choice is announced before the banner library loads', () => {
  const window = page(CONFIG, {
    cookie: stored(['necessary', 'analytics']),
    library: 'late',
  });
  assert.deepEqual(window.announcedBeforeLibrary, [
    { analytics: true, marketing: false },
  ]);
});

test('a choice is announced with only the categories a site shows', () => {
  const window = page(
    { ...CONFIG, categories: ['analytics'] },
    { cookie: stored(['necessary', 'analytics', 'marketing']) },
  );
  assert.deepEqual(window.announced, [{ analytics: true }]);
});

test('a choice made before the categories changed is not announced', () => {
  const window = page(CONFIG, {
    cookie: stored(['necessary', 'analytics'], 1),
  });
  assert.deepEqual(window.announced, []);
  assert.equal(window.runs[0].revision, 3);
});

test('a broken stored choice is ignored', () => {
  for (const cookie of [
    'cc_cookie=not-json',
    `cc_cookie=${encodeURIComponent('{"categories":"analytics"}')}`,
    `cc_cookie=${encodeURIComponent('{"categories":["analytics"],"revision":3}')}`,
  ]) {
    const window = page(CONFIG, { cookie });
    assert.deepEqual(window.announced, [], cookie);
    assert.equal(window.runs.length, 1);
  }
});

test("the visitor's choice and later changes are announced", () => {
  const window = page(CONFIG);
  const options = window.runs[0];
  options.onConsent({ cookie: { categories: ['necessary', 'analytics'] } });
  options.onChange({ cookie: { categories: ['necessary'] } });
  assert.deepEqual(window.announced, [
    { analytics: true, marketing: false },
    { analytics: false, marketing: false },
  ]);
});

test('the wording reaches the banner and its settings', () => {
  const { consentModal, preferencesModal } = english(page(CONFIG));
  assert.equal(consentModal.title, 'We use cookies');
  assert.equal(consentModal.description, 'Some cookies are needed.');
  assert.equal(consentModal.acceptAllBtn, 'Accept all');
  assert.equal(consentModal.acceptNecessaryBtn, 'Necessary only');
  assert.equal(consentModal.showPreferencesBtn, 'Customize');
  assert.equal(consentModal.footer, '');
  assert.equal(preferencesModal.title, 'Cookie settings');
  assert.equal(preferencesModal.savePreferencesBtn, 'Save my choices');
  assert.equal(preferencesModal.closeIconLabel, 'Close');
  assert.equal(preferencesModal.sections[2].title, 'Analytics');
  assert.equal(preferencesModal.sections[2].description, 'Counts visits.');
});

test('the privacy notice is linked from the banner and its settings', () => {
  const window = page({
    ...CONFIG,
    privacy: { url: '/privacy/', label: 'Privacy notice' },
  });
  const link = '<a href="/privacy/">Privacy notice</a>';
  assert.equal(english(window).consentModal.footer, link);
  assert.equal(
    english(window).preferencesModal.sections[0].description,
    `Some cookies are needed. ${link}`,
  );
});

test('wording and links are escaped, since the library writes them as HTML', () => {
  const window = page({
    ...CONFIG,
    text: {
      ...TEXT,
      title: '<img src=x onerror=alert(1)>',
      description: 'A & B',
    },
    privacy: { url: '/p/"><script>x</script>', label: '<b>Privacy</b>' },
  });
  const { consentModal } = english(window);
  assert.equal(consentModal.title, '&lt;img src=x onerror=alert(1)&gt;');
  assert.equal(consentModal.description, 'A &amp; B');
  assert.equal(
    consentModal.footer,
    '<a href="/p/&quot;&gt;&lt;script&gt;x&lt;/script&gt;">&lt;b&gt;Privacy&lt;/b&gt;</a>',
  );
});

test('the banner library in the package is the unmodified npm release', () => {
  for (const file of ['cookieconsent.umd.js', 'cookieconsent.css']) {
    const vendored = readFileSync(
      new URL(
        `../../src/wagtail_cookie_consent/static/wagtail_cookie_consent/vendor/${file}`,
        import.meta.url,
      ),
    );
    const released = readFileSync(
      new URL(
        `../../node_modules/vanilla-cookieconsent/dist/${file}`,
        import.meta.url,
      ),
    );
    assert.ok(vendored.equals(released), `${file} differs from npm's`);
  }
});
