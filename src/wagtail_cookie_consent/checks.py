from django.apps import apps
from django.core.checks import Error, Warning, register
from django.template import engines
from django.template.backends.django import DjangoTemplates


@register()
def settings_app_installed(app_configs, **kwargs):
    if apps.is_installed("wagtail.contrib.settings"):
        return []
    return [
        Error(
            "wagtail_cookie_consent needs wagtail.contrib.settings.",
            hint='Add "wagtail.contrib.settings" to INSTALLED_APPS.',
            id="wagtail_cookie_consent.E001",
        )
    ]


@register()
def request_context_processor_enabled(app_configs, **kwargs):
    """Without the request in the template context, the banner doesn't load."""
    django_engines = [
        engine for engine in engines.all() if isinstance(engine, DjangoTemplates)
    ]
    if not django_engines or any(
        "django.template.context_processors.request" in engine.engine.context_processors
        for engine in django_engines
    ):
        return []
    return [
        Warning(
            "wagtail_cookie_consent needs the request in the template context, "
            "or the banner doesn't load.",
            hint='Add "django.template.context_processors.request" to the '
            "context_processors of your TEMPLATES setting.",
            id="wagtail_cookie_consent.W001",
        )
    ]
