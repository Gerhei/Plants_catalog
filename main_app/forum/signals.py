from django.db.models.signals import post_save
from django.db.models import ObjectDoesNotExist
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ForumUsers, Posts

@receiver(post_save, sender=User)
def create_forum_user(sender, instance,**kwargs):
    try:
        forum_user=ForumUsers.objects.get(user=instance)
    except ObjectDoesNotExist:
        forum_user=ForumUsers(user=instance)
        forum_user.save()