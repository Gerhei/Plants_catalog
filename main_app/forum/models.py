from django.shortcuts import reverse

from django.db import models
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy

from main_app.settings import MAX_USERNAME_LENGTH

from slugify import slugify
from datetime import timedelta, datetime
import os

"""
 SQLite does not support case-insensitive lookups.
 Therefore, to be able to conduct a case-insensitive search, 
 we must have a name in lower case (name_lower)
"""

class Sections(models.Model):
    name = models.CharField(max_length=40, unique=True, verbose_name=_('name'))
    name_lower = models.CharField(max_length=40, editable=False)
    slug = models.SlugField(max_length=60, unique=True, db_index=True,
                            editable=False, verbose_name='URL')
    order = models.SmallIntegerField(default=0, db_index=True,
                                     editable=False, verbose_name=_('order'))
    super_sections = models.ForeignKey('Sections', on_delete=models.PROTECT, null=True,
                                       blank=True, verbose_name=_('super section'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('topics', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        if self.super_sections:
            self.order = self.super_sections.order + 1
        self.slug = slugify(self.name)
        super(Sections, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("section")
        verbose_name_plural = _("sections")
        ordering = ('name',)


def forumusers_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.username_lower, ext)
    return os.path.join('forum/user_images', filename)

class ForumUsers(models.Model):
    username_lower = models.CharField(max_length=MAX_USERNAME_LENGTH, editable=False)
    slug = models.SlugField(max_length=MAX_USERNAME_LENGTH, unique=True, db_index=True,
                            editable=False, verbose_name='URL')
    user_image = models.ImageField(blank=True, upload_to=forumusers_file_name,
                                 default='/forum/user_images/default_profile.jpg',
                                 verbose_name=_('profile image'))
    about_user = models.TextField(blank=True, verbose_name=_('about user'))
    reputation = models.IntegerField(default=0, verbose_name=_('reputation'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('user'))

    def __str__(self):
        return self.username_lower

    def get_absolute_url(self):
        return reverse('profile', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        self.username_lower = self.user.username.lower()
        super(ForumUsers, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ('username_lower',)


class Statistics(models.Model):
    """
     Stores view statistics for topic and post user ratings for each user.
     For educational purposes (using contenttypes)
     these 2 types of statistics are combined in one model.
    """
    value_type = models.IntegerField(choices=((0, _("Rate")), (1, _("Views"))), editable=False,
                                     verbose_name=_("type of statistics"))
    value = models.IntegerField(default=0, verbose_name=_("value of statistics"))
    user = models.ForeignKey(ForumUsers, on_delete=models.CASCADE, verbose_name=_("user"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_("model"))
    object_id = models.PositiveIntegerField(verbose_name=_("ID record"))
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.user} {self.content_type}-{self.object_id}'

    def save(self, *args, **kwargs):
        """
         Check the model class and on the basis of this assign the type of statistics.
         Then change this statistics.
        """
        if self.content_object.__class__ == Posts:
            self.value_type = 0
            self.change_post_rate()
        elif self.content_object.__class__ == Topics:
            self.value_type = 1
            self.change_view_count()
        else:
            raise ValidationError("%s does not support statistics for the %s model"
                                  % (self.__class__.__name__, self.content_object.__class__.__name__))
        super(Statistics, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
         Check the model class and on the basis of this assign the type of statistics.
         Then change this statistics.
        """
        if self.value_type == 0 and self.content_object.__class__ == Posts:
            self.change_post_rate(is_delete=True)
        elif self.value_type == 1 and self.content_object.__class__ == Topics:
            self.change_view_count(is_delete=True)
        super(Statistics, self).delete(*args, **kwargs)

    """  
     Since each instance of the model is related to the statistics 
     of only one user and one instance content_object model,   
     the resulting statistic is stored in the associated model (view_count of topic for example).
     therefore, when deleting statistics instance, we must change these related fields. 
     The following 2 methods perform this function.
    """

    def change_view_count(self, is_delete=False):
        # subtract current statistics value when deleting
        direction_change = -1 if is_delete else 1

        # change related field
        self.content_object.view_count = F('view_count') + self.value * direction_change
        self.content_object.save()

    def change_post_rate(self, is_delete=False):
        # subtract current statistics value when deleting
        direction_change = -1 if is_delete else 1

        # change related field
        user = self.content_object.author
        user.reputation = F('reputation') + self.value * direction_change
        user.save()

    class Meta:
        verbose_name = _("statistics")
        verbose_name_plural = _("statistics")
        ordering = ('value_type', 'user', 'object_id')

        # this condition contains the whole meaning of the model.
        # each user can view a concrete topic only once and have only one rating for a concrete post
        unique_together = (('user', 'value_type', 'object_id'),)


class Topics(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('title'))
    name_lower = models.CharField(max_length=100, editable=False)
    slug = models.SlugField(max_length=100, unique=True, db_index=True,
                            editable=False, verbose_name='URL')
    view_count = models.IntegerField(validators=(MinValueValidator(0),), editable=False,
                                     default=0, verbose_name=_("views count"))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_('time create'))
    author = models.ForeignKey(ForumUsers, on_delete=models.SET_NULL, null=True, verbose_name=_('author'))
    sections = models.ForeignKey(Sections, on_delete=models.PROTECT, verbose_name=_('section'))
    statistics = GenericRelation(Statistics, related_query_name='topics')

    def __str__(self):
        return f'{self.name}-{self.pk}'

    def get_absolute_url(self):
        return reverse('topic', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # The parent method is called twice,
        # since it is necessary to get the pk to create the slug, and then save it
        super(Topics, self).save(*args, **kwargs)

        # We use refresh_from_db because the views use the F class to increase the view_count
        # and due to a double call to the super().save method, a double change in the view_count is possible
        self.refresh_from_db()

        self.slug = slugify(f'{self.name}_{self.pk}')
        self.name_lower = self.name.lower()
        super(Topics, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("topic")
        verbose_name_plural = _("topics")
        ordering = ('-time_create', 'name')


class Posts(models.Model):
    text = models.TextField(max_length=15000, verbose_name=_('post'))
    post_type = models.IntegerField(choices=((0,'question'), (1,'answer')))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_('time create'))
    time_update = models.DateTimeField(auto_now=True, verbose_name=_('time update'))
    author = models.ForeignKey(ForumUsers, on_delete=models.SET_NULL,
                               null=True, verbose_name=_('author'))
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE, verbose_name=_('topic'))
    statistics = GenericRelation(Statistics, related_query_name='posts')

    def __str__(self):
        return '%s-%s' % (_("Post"), self.pk)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.post_type==0:
            try:
                question = Posts.objects.get(topic=self.topic, post_type=0)
            except MultipleObjectsReturned:
                raise ValidationError({
                    'post_type': _(
                        'There is already more than 1 question in the topic.'
                    ),
                })
            except ObjectDoesNotExist:
                pass
            else:
                raise ValidationError({
                    'post_type': _(
                        'There can\'t be more than one question in one topic.'
                     ),
                })


    def is_changed(self):
        return self.time_update - self.time_create > timedelta(seconds=1)

    def is_editable(self):
        return datetime.now() - self.time_create < timedelta(minutes=10)

    def is_user_can_edit(self, forum_user):
        if forum_user:
            return self.is_editable() and self.author==forum_user

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        ordering = ('topic', 'post_type', 'time_create', 'author')


def posts_file_name(instance, filename):
    filename = "post_%s/%s" % (instance.post.pk,filename)
    return os.path.join('forum/posts_attached_files', filename)

class AttachedFiles(models.Model):
    allowed_ext = ['jpeg', 'jpg', 'png', 'jfif', 'bmp', 'svg', 'tif',
                   'txt', 'doc', 'docx', 'xlsx', 'pptx']
    text_ext = ['txt', 'doc', 'docx', 'xlsx', 'pptx']
    max_files_per_post = 10

    file = models.FileField(validators=(FileExtensionValidator(allowed_extensions=allowed_ext),),
                            upload_to=posts_file_name, verbose_name=_("file"))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_('time create'))
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, verbose_name=_("post"))

    def __str__(self):
        return self.file.name

    def get_absolute_url(self):
        return self.file.url

    def clean(self):
        count_files = AttachedFiles.objects.filter(post=self.post).count()
        if count_files >= self.max_files_per_post:
            raise ValidationError({'file': format_lazy('{message} = {number_files}',
                                                       message= _('The allowed number of '
                                                                  'attached files has been exceeded for this post '),
                                                       number_files=self.max_files_per_post)})

    class Meta:
        verbose_name = _("attached file")
        verbose_name_plural = _("attached files")
        ordering = ('time_create',)
