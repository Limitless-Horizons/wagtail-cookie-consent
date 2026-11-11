from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailCookieConsentAppConfig(AppConfig):
    label = "wagtail_cookie_consent"
    name = "wagtail_cookie_consent"
    verbose_name = _("Cookie consent")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import checks  # noqa: F401
