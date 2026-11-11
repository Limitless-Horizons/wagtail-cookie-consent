from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting(icon="lock")
class CookieConsentSettings(BaseSiteSetting):
    class ShowTo(models.TextChoices):
        EVERYONE = "everyone", _("Everyone")
        NO_ONE = "no_one", _("No one")

    show_to = models.CharField(
        _("show the banner to"),
        max_length=20,
        choices=ShowTo.choices,
        default=ShowTo.EVERYONE,
        help_text=_(
            "Everyone: each visitor gets the banner on their first visit. "
            "No one: the banner and the Cookie settings link are off."
        ),
    )
    show_analytics = models.BooleanField(
        _("analytics"),
        default=True,
        help_text=_(
            "When this is on, visitors choose whether to allow analytics cookies."
        ),
    )
    show_marketing = models.BooleanField(
        _("marketing"),
        default=True,
        help_text=_(
            "When this is on, visitors choose whether to allow marketing cookies, "
            "such as those of embedded videos and ads."
        ),
    )
    title = models.CharField(
        _("title"),
        max_length=255,
        blank=True,
        help_text=_('Leave it blank for the default: "We use cookies".'),
    )
    text = models.TextField(
        _("text"),
        blank=True,
        help_text=_("Leave it blank for the default text."),
    )
    privacy_page = models.ForeignKey(
        "wagtailcore.Page",
        verbose_name=_("privacy notice"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("The banner links to this page."),
    )

    select_related = ["privacy_page"]

    panels = [
        FieldPanel("show_to"),
        MultiFieldPanel(
            [
                FieldPanel("show_analytics"),
                FieldPanel("show_marketing"),
            ],
            heading=_("Categories shown"),
            help_text=_(
                "Necessary cookies are always on, and visitors aren't asked about "
                "them. With neither category checked there's nothing to ask, so "
                "the banner is off."
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("text"),
                FieldPanel("privacy_page"),
            ],
            heading=_("Wording"),
        ),
    ]

    class Meta:
        verbose_name = _("Cookie consent")
        verbose_name_plural = _("Cookie consent")

    def categories(self):
        """The categories visitors are asked about, in the banner's order."""
        shown = []
        if self.show_analytics:
            shown.append("analytics")
        if self.show_marketing:
            shown.append("marketing")
        return shown

    def revision(self):
        """A number that changes when the categories shown change. A visitor's
        stored choice counts only for the revision it was made under, so
        they're asked again when what's asked changes."""
        return (1 if self.show_analytics else 0) + (2 if self.show_marketing else 0)

    def banner_is_on(self):
        return self.show_to == self.ShowTo.EVERYONE and bool(self.categories())
