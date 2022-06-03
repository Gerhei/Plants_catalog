from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PlantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plants'
    verbose_name = _("plants")
