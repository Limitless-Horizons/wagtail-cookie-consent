"""
What the {% cookie_consent %} template tag renders: whether the banner is on
for this request, and the configuration the browser script gets.
"""

from django.conf import settings
from django.utils.translation import gettext as _

from .models import CookieConsentSettings


def get_settings(request):
    """This site's settings, or the defaults when the request has no site."""
    try:
        return CookieConsentSettings.for_request(request)
    except CookieConsentSettings.DoesNotExist:
        return CookieConsentSettings()


def banner_settings(context):
    """This site's settings when the banner is on for this request, or None:
    no request, a preview, "No one", or no category to ask about."""
    request = context.get("request")
    if request is None or getattr(request, "is_preview", False):
        return None
    site_settings = get_settings(request)
    return site_settings if site_settings.banner_is_on() else None


def wording(site_settings):
    """The banner's text. The title and text come from the admin when they're
    set there; everything else is translatable default wording."""
    return {
        "title": site_settings.title or _("We use cookies"),
        "description": site_settings.text
        or _(
            "Some cookies are needed for this site to work. With your "
            "permission, we'd also like to use optional cookies. You can change "
            "your choice at any time under Cookie settings."
        ),
        "acceptAll": _("Accept all"),
        "necessaryOnly": _("Necessary only"),
        "customize": _("Customize"),
        "settingsTitle": _("Cookie settings"),
        "save": _("Save my choices"),
        "close": _("Close"),
        "necessaryTitle": _("Necessary"),
        "necessaryText": _(
            "Needed for the site to work, such as keeping you signed in and "
            "protecting forms. They're always on."
        ),
        "analyticsTitle": _("Analytics"),
        "analyticsText": _(
            "Help us understand how the site is used, so we can improve it."
        ),
        "marketingTitle": _("Marketing"),
        "marketingText": _(
            "Used by embedded content, such as videos, and by advertising."
        ),
    }


def privacy_link(site_settings, request):
    page = site_settings.privacy_page
    if page is None:
        return None
    # On a site in several languages, the page in the visitor's language.
    page = page.localized
    if not page.live:
        return None
    return {"url": page.get_url(request), "label": page.title}


def banner_config(context):
    """The browser script's configuration, or None when the banner is off."""
    site_settings = banner_settings(context)
    if site_settings is None:
        return None
    return {
        "categories": site_settings.categories(),
        "revision": site_settings.revision(),
        "text": wording(site_settings),
        "privacy": privacy_link(site_settings, context["request"]),
        "hideFromBots": getattr(
            settings, "WAGTAIL_COOKIE_CONSENT_HIDE_FROM_BOTS", True
        ),
    }
