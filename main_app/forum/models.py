from django.shortcuts import reverse
from django.db import models
from django.db.models import Count, F, Value, Q
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from main_app.settings import MEDIA_URL
from slugify import slugify
from datetime import timedelta,datetime
import os

class Sections(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    name_lower = models.CharField(max_length=255, editable=False)
    order=models.SmallIntegerField(default=0,db_index=True,editable=False,verbose_name='Порядок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=False, verbose_name='URL')
    super_sections=models.ForeignKey('Sections',on_delete=models.PROTECT,null=True,blank=True,verbose_name='Надраздел')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('topics', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        self.name_lower=self.name.lower()
        if self.super_sections:
            self.order=self.super_sections.order+1
        self.slug=slugify(f'{self.name}')
        super(Sections, self).save(*args, **kwargs)

    class Meta:
        verbose_name="Раздел"
        verbose_name_plural="Разделы"


def forumusers_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.username_lower, ext)
    return os.path.join('forum/user_images', filename)

class ForumUsers(models.Model):
    username_lower = models.CharField(max_length=255, editable=False)
    user_image=models.ImageField(blank=True,upload_to=forumusers_file_name, default='/forum/user_images/default_profile.jpg',
                                 verbose_name='Изображение профиля')
    about_user=models.TextField(blank=True,verbose_name='О пользователе')
    reputation=models.IntegerField(default=0,verbose_name='Репутация')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=False, verbose_name='URL')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.username_lower

    def get_absolute_url(self):
        return reverse('profile', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        self.slug=slugify(self.user.username)
        self.username_lower=self.user.username.lower()
        super(ForumUsers, self).save(*args, **kwargs)

    class Meta:
        verbose_name="Пользователь"
        verbose_name_plural="Пользователи"
        ordering=['username_lower']


# stores view statistics for topic, post user ratings
# for educational purposes (using contenttypes)
# these 2 types of statistics are combined in one model.
class Statistics(models.Model):
    user = models.ForeignKey(ForumUsers, on_delete=models.CASCADE, verbose_name="Пользователь")
    value_type = models.IntegerField(choices=((0, "Оценка"), (1, "Просмотр")), editable=False,
                                     verbose_name="Тип статистики")
    value = models.IntegerField(default=0, verbose_name="Значение статистики")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Модель")
    object_id = models.PositiveIntegerField(verbose_name="ID записи")
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.user} {self.content_type}-{self.object_id}'

    def save(self, *args, **kwargs):
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
        if self.value_type == 0 and self.content_object.__class__ == Posts:
            self.change_post_rate(is_delete=True)
        elif self.value_type == 1 and self.content_object.__class__ == Topics:
            self.change_view_count(is_delete=True)
        super(Statistics, self).delete(*args, **kwargs)

    def change_view_count(self, is_delete=False):
        direction_change = -1 if is_delete else 1
        self.content_object.view_count = F('view_count') + self.value * direction_change
        self.content_object.save()

    def change_post_rate(self, is_delete=False):
        direction_change = -1 if is_delete else 1
        user = self.content_object.author
        user.reputation = F('reputation') + self.value * direction_change
        user.save()

    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"
        ordering = ['value_type', 'user', 'object_id']
        unique_together = [['user', 'value_type', 'object_id']]


class Topics(models.Model):
    name=models.CharField(max_length=255,verbose_name='Заголовок')
    name_lower = models.CharField(max_length=255, editable=False)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=False, verbose_name='URL')
    view_count=models.IntegerField(validators=[MinValueValidator(0)],editable=False,default=0,verbose_name="Количество просмотров")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    author=models.ForeignKey(ForumUsers,on_delete=models.SET_NULL, null=True,verbose_name='Автор')
    sections=models.ForeignKey(Sections,on_delete=models.PROTECT,verbose_name='Раздел')
    statistics = GenericRelation(Statistics,related_query_name='topics')

    def __str__(self):
        return f'{self.name}-{self.pk}'

    def get_absolute_url(self):
        return reverse('topic', kwargs={'slug_topic':self.slug})

    def save(self, *args, **kwargs):
        # The parent method is called twice,
        # since it is necessary to get the pk to create the slug,
        # and then save it
        super(Topics, self).save(*args, **kwargs)
        # We use refresh_from_db because the controllers use the F class to increase the view_count.
        # and due to a double call to the super().save method, a double change in the view_count is possible
        self.refresh_from_db()
        self.slug=slugify(f'{self.name}_{self.pk}')
        self.name_lower=self.name.lower()
        super(Topics, self).save(*args, **kwargs)

    class Meta:
        verbose_name="Тема"
        verbose_name_plural="Темы"
        ordering=['time_create', 'name']


class Posts(models.Model):
    author=models.ForeignKey(ForumUsers,on_delete=models.SET_NULL, null=True,verbose_name='Автор')
    topic=models.ForeignKey(Topics,on_delete=models.CASCADE,verbose_name='Тема')
    text=models.TextField(verbose_name='Сообщение')
    # needed to find the topic author
    post_type=models.IntegerField(choices=((0,'question'),(1,'answer')))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    statistics = GenericRelation(Statistics, related_query_name='posts')

    def __str__(self):
        return f'Сообщение-{self.pk}'

    def is_changed(self):
        return self.time_update-self.time_create > timedelta(seconds=1)

    def is_editable(self):
        return datetime.now()-self.time_create < timedelta(minutes=10)

    class Meta:
        verbose_name="Сообщение"
        verbose_name_plural="Сообщения"
        ordering=['topic','time_create','author']


def posts_file_name(instance, filename):
    filename = "post_%s/%s" % (instance.post.pk,filename)
    return os.path.join('forum/posts_attached_files', filename)

class AttachedFiles(models.Model):
    allowed_ext = ['jpeg', 'jpg', 'png', 'jfif', 'bmp', 'svg', 'tif',
                   'txt', 'doc', 'docx', 'xlsx', 'pptx']

    max_files_per_post = 10

    file = models.FileField(upload_to = posts_file_name,
                          validators = [FileExtensionValidator(allowed_extensions = allowed_ext)],
                          verbose_name = "Файл")
    time_create = models.DateTimeField(auto_now_add = True, verbose_name = 'Дата создания')
    post = models.ForeignKey(Posts,on_delete = models.CASCADE,verbose_name = "Сообщение")

    def __str__(self):
        return self.file.name

    def get_absolute_url(self):
        return self.file.url

    def clean(self):
        count_files=AttachedFiles.objects.filter(post=self.post).count()
        if count_files>=self.max_files_per_post:
            raise ValidationError({'file': ('Для данного сообщения превышено допустимое '
                                            'количество прикрепленных файлов = %s') % self.max_files_per_post})

    class Meta:
        verbose_name = "Прикрепленный файл"
        verbose_name_plural = "Прикрепленные файлы"
        ordering = ['time_create']