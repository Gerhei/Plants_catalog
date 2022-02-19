from django.db import models
from django.core.validators import MinValueValidator
from  django.shortcuts import reverse
from django.contrib.auth.models import User
from slugify import slugify

class SuperSectionsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_sections__isnull=True)

class SubSectionsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_sections__isnull=False)

# Create your models here.
class Sections(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    name_lower = models.CharField(max_length=255, editable=False)
    order=models.SmallIntegerField(default=0,db_index=True,verbose_name='Порядок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=False, verbose_name='URL')
    super_sections=models.ForeignKey('SuperSections',on_delete=models.PROTECT,null=True,blank=True,verbose_name='Надраздел')

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('plant', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        super(Sections, self).save(*args, **kwargs)
        self.slug=slugify(f'{self.name}_{self.order}')
        self.name_lower=self.name.lower()
        super(Sections, self).save(*args, **kwargs)

    class Meta:
        verbose_name="Раздел"
        verbose_name_plural="Разделы"
        unique_together = ['name', 'order']

class SuperSections(Sections):
    objects=SuperSectionsManager()
    class Meta:
        proxy=True
        ordering = ['order', 'name']

class SubSections(Sections):
    objects = SubSectionsManager()

    def __str__(self):
        f'{self.super_sections.name}-{self.name}'

    class Meta:
        proxy=True
        ordering=['super_sections__order','super_sections__name','order','name']


class ForumUsers(models.Model):
    username_lower = models.CharField(max_length=255, editable=False)
    user_image=models.ImageField(blank=True,verbose_name='Изображение профиля')
    about_user=models.TextField(blank=True,verbose_name='О пользователе')
    reputation=models.IntegerField(default=0,verbose_name='Репутация')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=False, verbose_name='URL')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    # def get_absolute_url(self):
    #     return reverse('plant', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        self.slug=slugify(self.user.username)
        self.username_lower=self.user.username.lower()
        super(ForumUsers, self).save(*args, **kwargs)

    class Meta:
        verbose_name="Пользователь"
        verbose_name_plural="Пользователи"
        ordering=['username_lower']

class Topics(models.Model):
    name=models.CharField(max_length=255,verbose_name='Заголовок')
    name_lower = models.CharField(max_length=255, editable=False)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=False, verbose_name='URL')
    view_count=models.IntegerField(validators=[MinValueValidator(0)],default=0)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    author=models.ForeignKey(ForumUsers,on_delete=models.SET_NULL, null=True,verbose_name='Автор')
    sections=models.ForeignKey(Sections,on_delete=models.PROTECT,verbose_name='Раздел')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('topic', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        super(Topics, self).save(*args, **kwargs)
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
    post_type=models.IntegerField(choices=((0,'question'),(1,'answer')))
    score=models.IntegerField(default=0,verbose_name='Рейтинг')
    #attached_files=
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return f'{self.author}:{self.topic}'

    class Meta:
        verbose_name="Сообщение"
        verbose_name_plural="Сообщения"
        ordering=['topic','time_create','author']