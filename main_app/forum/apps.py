from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ForumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forum'
    verbose_name = _("forum")

    def ready(self):
        # need for post_save signal for create forum user when create default user
        from . import signals
