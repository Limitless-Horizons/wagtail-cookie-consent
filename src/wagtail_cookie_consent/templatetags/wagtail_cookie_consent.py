from django import template
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.translation import gettext as _

from ..banner import banner_config, banner_settings


register = template.Library()


@register.inclusion_tag(
    "wagtail_cookie_consent/cookie_consent.html", takes_context=True
)
def cookie_consent(context):
    """The consent banner. It renders nothing when the banner is off."""
    return {"config": banner_config(context)}


@register.simple_tag(takes_context=True)
def cookie_settings_link(context, label=None, **attrs):
    """A button that reopens the banner's settings, so a visitor can change
    their choice. It renders nothing when the banner is off. Keyword arguments
    become HTML attributes, for example class="..."."""
    if banner_settings(context) is None:
        return ""
    return format_html(
        '<button type="button" data-cc="show-preferencesModal"{}>{}</button>',
        flatatt(attrs),
        label or _("Cookie settings"),
    )
