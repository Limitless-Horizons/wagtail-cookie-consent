# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-11-12

### Changed

- README: screenshots of the banner, the visitor's choices and the settings in the Wagtail admin.

## [0.1.0] - 2026-11-11

### Added

- A cookie consent banner, built on vanilla-cookieconsent 3.3.0, which ships inside the package.
- Cookie consent settings for each site in the Wagtail admin (Settings → Cookie consent): who sees the banner, which categories it asks about, its title and text, and a privacy notice page.
- The `{% cookie_consent %}` template tag, which loads the banner, except in previews.
- The `{% cookie_settings_link %}` template tag, a button that reopens the visitor's choices.
- The `wagtail-cookie-consent:change` event, which announces the visitor's choice to the page.
- Visitors are asked again when a site changes the categories it shows.
- System checks for `wagtail.contrib.settings` and the request context processor.
- `WAGTAIL_COOKIE_CONSENT_HIDE_FROM_BOTS`, a Django setting for showing the banner in browser tests.
- Support for Wagtail 7.4, 8.0 and 8.1.

[Unreleased]: https://github.com/Limitless-Horizons/wagtail-cookie-consent/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/Limitless-Horizons/wagtail-cookie-consent/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Limitless-Horizons/wagtail-cookie-consent/releases/tag/v0.1.0
