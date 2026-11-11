import json
import re

import pytest

from django.contrib.auth.models import AnonymousUser
from django.core.checks import run_checks
from django.template import Context, Template
from django.test import RequestFactory, override_settings
from django.utils import translation
from wagtail.models import Locale, Site

from wagtail_cookie_consent.models import CookieConsentSettings
from wagtail_cookie_consent.test.models import PlainPage


pytestmark = pytest.mark.django_db

CONFIG = re.compile(
    r'<script id="wagtail-cookie-consent-config" type="application/json">(.*?)</script>',
    re.S,
)
SETTINGS_LINK = '<button type="button" data-cc="show-preferencesModal"'


def config_in(html):
    match = CONFIG.search(html)
    assert match, "no banner config in the page"
    return json.loads(match.group(1))


@pytest.fixture
def site():
    return Site.objects.get(is_default_site=True)


@pytest.fixture
def consent_settings(site):
    return CookieConsentSettings.for_site(site)


@pytest.fixture
def plain_page(site):
    page = PlainPage(title="Plain", slug="plain")
    site.root_page.add_child(instance=page)
    return page


def anonymous_request(path="/"):
    request = RequestFactory().get(path)
    request.user = AnonymousUser()
    return request


def render(template, request, **context):
    return Template("{% load wagtail_cookie_consent %}" + template).render(
        Context({"request": request, **context})
    )


# Whether the banner is on


def test_banner_is_on_by_default(client, plain_page):
    html = client.get(plain_page.url).content.decode()
    assert config_in(html)["categories"] == ["analytics", "marketing"]
    assert "wagtail_cookie_consent/js/cookie-consent.js" in html
    assert "wagtail_cookie_consent/vendor/cookieconsent.umd.js" in html
    assert "wagtail_cookie_consent/vendor/cookieconsent.css" in html
    assert SETTINGS_LINK in html


def test_no_one_turns_the_banner_and_link_off(client, consent_settings, plain_page):
    consent_settings.show_to = CookieConsentSettings.ShowTo.NO_ONE
    consent_settings.save()
    html = client.get(plain_page.url).content.decode()
    assert not CONFIG.search(html)
    assert "cookieconsent" not in html
    assert SETTINGS_LINK not in html


def test_no_categories_turns_the_banner_off(client, consent_settings, plain_page):
    consent_settings.show_analytics = False
    consent_settings.show_marketing = False
    consent_settings.save()
    html = client.get(plain_page.url).content.decode()
    assert not CONFIG.search(html)
    assert SETTINGS_LINK not in html


def test_no_banner_in_previews(plain_page):
    request = anonymous_request()
    request.is_preview = True
    html = render("{% cookie_consent %}{% cookie_settings_link %}", request)
    assert html.strip() == ""


def test_no_banner_without_request():
    html = Template(
        "{% load wagtail_cookie_consent %}{% cookie_consent %}{% cookie_settings_link %}"
    ).render(Context())
    assert html.strip() == ""


def test_no_site_uses_defaults(consent_settings):
    consent_settings.show_to = CookieConsentSettings.ShowTo.NO_ONE
    consent_settings.save()
    request = anonymous_request()
    request.META["HTTP_HOST"] = "unknown.example"
    Site.objects.update(is_default_site=False)
    assert config_in(render("{% cookie_consent %}", request))["categories"] == [
        "analytics",
        "marketing",
    ]


def test_each_site_has_its_own_settings(site, consent_settings):
    other = Site.objects.create(
        hostname="other.example", root_page=site.root_page, site_name="Other"
    )
    other_settings = CookieConsentSettings.for_site(other)
    other_settings.show_to = CookieConsentSettings.ShowTo.NO_ONE
    other_settings.save()

    request = anonymous_request()
    request.META["HTTP_HOST"] = "other.example"
    assert render("{% cookie_consent %}", request).strip() == ""
    assert config_in(render("{% cookie_consent %}", anonymous_request()))


# Categories


def test_only_checked_categories_are_shown(client, consent_settings, plain_page):
    consent_settings.show_marketing = False
    consent_settings.save()
    config = config_in(client.get(plain_page.url).content.decode())
    assert config["categories"] == ["analytics"]


def test_revision_follows_the_categories_shown(client, consent_settings, plain_page):
    assert config_in(client.get(plain_page.url).content.decode())["revision"] == 3
    consent_settings.show_marketing = False
    consent_settings.save()
    assert config_in(client.get(plain_page.url).content.decode())["revision"] == 1
    consent_settings.show_analytics = False
    consent_settings.show_marketing = True
    consent_settings.save()
    assert config_in(client.get(plain_page.url).content.decode())["revision"] == 2


# Wording


def test_default_wording(client, plain_page):
    text = config_in(client.get(plain_page.url).content.decode())["text"]
    assert text["title"] == "We use cookies"
    assert text["description"].startswith("Some cookies are needed")
    assert text["acceptAll"] == "Accept all"
    assert text["necessaryOnly"] == "Necessary only"
    assert text["customize"] == "Customize"


def test_title_and_text_from_the_admin(client, consent_settings, plain_page):
    consent_settings.title = "Cookies & you"
    consent_settings.text = "We'd like to count visits."
    consent_settings.save()
    text = config_in(client.get(plain_page.url).content.decode())["text"]
    assert text["title"] == "Cookies & you"
    assert text["description"] == "We'd like to count visits."


def test_admin_text_cannot_break_out_of_the_config(
    client, consent_settings, plain_page
):
    consent_settings.title = "</script><script>alert(1)</script>"
    consent_settings.save()
    html = client.get(plain_page.url).content.decode()
    assert "<script>alert(1)" not in html
    assert config_in(html)["text"]["title"] == "</script><script>alert(1)</script>"


# Privacy notice link


def test_no_privacy_link_by_default(client, plain_page):
    assert config_in(client.get(plain_page.url).content.decode())["privacy"] is None


def test_privacy_link_to_a_live_page(client, site, consent_settings, plain_page):
    privacy = PlainPage(title="Privacy notice", slug="privacy")
    site.root_page.add_child(instance=privacy)
    consent_settings.privacy_page = privacy
    consent_settings.save()
    config = config_in(client.get(plain_page.url).content.decode())
    assert config["privacy"] == {"url": privacy.url, "label": "Privacy notice"}


def test_no_privacy_link_to_an_unpublished_page(
    client, site, consent_settings, plain_page
):
    privacy = PlainPage(title="Privacy notice", slug="privacy", live=False)
    site.root_page.add_child(instance=privacy)
    consent_settings.privacy_page = privacy
    consent_settings.save()
    assert config_in(client.get(plain_page.url).content.decode())["privacy"] is None


def test_privacy_link_follows_the_language(settings, site, consent_settings):
    settings.WAGTAIL_I18N_ENABLED = True
    settings.WAGTAIL_CONTENT_LANGUAGES = [("en", "English"), ("fr", "French")]
    privacy = PlainPage(title="Privacy notice", slug="privacy")
    site.root_page.add_child(instance=privacy)
    french = privacy.copy_for_translation(
        Locale.objects.create(language_code="fr"), copy_parents=True
    )
    french.title = "Confidentialité"
    french.save_revision().publish()
    consent_settings.privacy_page = privacy
    consent_settings.save()

    with translation.override("fr"):
        config = config_in(render("{% cookie_consent %}", anonymous_request()))
    assert config["privacy"]["label"] == "Confidentialité"


# The Cookie settings link


def test_settings_link_default():
    html = render("{% cookie_settings_link %}", anonymous_request())
    assert html == (
        '<button type="button" data-cc="show-preferencesModal">Cookie settings</button>'
    )


def test_settings_link_with_label_and_attributes():
    html = render(
        '{% cookie_settings_link "Cookies" class="footer-link" id="cookies" %}',
        anonymous_request(),
    )
    assert html == (
        '<button type="button" data-cc="show-preferencesModal" '
        'class="footer-link" id="cookies">Cookies</button>'
    )


def test_settings_link_escapes_its_label_and_attributes():
    html = render(
        "{% cookie_settings_link label class=css %}",
        anonymous_request(),
        label="<b>Cookies</b>",
        css='x" onclick="alert(1)',
    )
    assert "<b>" not in html
    assert 'onclick="alert' not in html


# Automated browsers


def test_banner_hides_from_bots_by_default(client, plain_page):
    assert (
        config_in(client.get(plain_page.url).content.decode())["hideFromBots"] is True
    )


@override_settings(WAGTAIL_COOKIE_CONSENT_HIDE_FROM_BOTS=False)
def test_setting_shows_the_banner_to_bots(client, plain_page):
    assert (
        config_in(client.get(plain_page.url).content.decode())["hideFromBots"] is False
    )


# Installation


def test_system_check_passes():
    assert not [
        error for error in run_checks() if error.id.startswith("wagtail_cookie_consent")
    ]


def test_system_check_needs_the_settings_app(settings):
    settings.INSTALLED_APPS = [
        app for app in settings.INSTALLED_APPS if app != "wagtail.contrib.settings"
    ]
    assert [
        error.id
        for error in run_checks()
        if error.id.startswith("wagtail_cookie_consent")
    ] == ["wagtail_cookie_consent.E001"]


def test_system_check_warns_without_the_request_context_processor(settings):
    templates = [dict(engine) for engine in settings.TEMPLATES]
    templates[0]["OPTIONS"] = {
        "context_processors": [
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]
    }
    settings.TEMPLATES = templates
    assert [
        error.id
        for error in run_checks()
        if error.id.startswith("wagtail_cookie_consent")
    ] == ["wagtail_cookie_consent.W001"]
