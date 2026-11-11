"""Checks an installed wagtail-cookie-consent package has everything it needs."""

import sys

from importlib.metadata import version
from importlib.resources import files


package = files("wagtail_cookie_consent")
if "/site-packages/" not in str(package):
    sys.exit(f"Not the installed package: {package}")

missing = [
    path
    for path in (
        "templates/wagtail_cookie_consent/cookie_consent.html",
        "templatetags/wagtail_cookie_consent.py",
        "static/wagtail_cookie_consent/js/cookie-consent.js",
        "static/wagtail_cookie_consent/vendor/cookieconsent.umd.js",
        "static/wagtail_cookie_consent/vendor/cookieconsent.css",
        "static/wagtail_cookie_consent/vendor/LICENSE",
        "migrations/0001_initial.py",
    )
    if not package.joinpath(path).is_file()
]
if missing:
    sys.exit(f"Missing from the package: {', '.join(missing)}")

print(f"wagtail-cookie-consent {version('wagtail-cookie-consent')}: package complete")
