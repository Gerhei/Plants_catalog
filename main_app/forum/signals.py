from django.db.models.signals import post_save
from django.db.models import ObjectDoesNotExist
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ForumUsers, Posts

@receiver(post_save, sender=User)
def create_forum_user(sender, instance, **kwargs):
    """
    Since the forum user model is linked to the default user model,
    we need to ensure that the forum users instance is created when created user model instance
    """
    try:
        forum_user = ForumUsers.objects.get(user=instance)
    except ObjectDoesNotExist:
        # if there is no forum user for the user instance
        forum_user = ForumUsers(user=instance)
        forum_user.save()