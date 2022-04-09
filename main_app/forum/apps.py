from django.apps import AppConfig


class ForumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forum'
    verbose_name = "Форум"

    def ready(self):
        # need for post_save signal for create forum user when create default user
        from . import signals