from django.db import models
from  django.shortcuts import reverse
from slugify import slugify
import os

PRIORITIES = (
    (0, 'Домен'), (1, 'Надцарство'), (2, 'Царство'), (3, 'Подцарство'), (4, 'Клада'),
    (5, 'Надотдел'), (6, 'Отдел'), (7, 'Подотдел'), (8, 'Надкласс'), (9, 'Класс'),
    (10, 'Подкласс'), (11, 'Надпорядок'), (12, 'Порядок'), (13, 'Ряд'), (14, 'Тип'),
    (15, 'Семейство'), (16, 'Подсемейство'), (17, 'Надтриба'), (18, 'Триба'),
    (19, 'Подтриба'), (20, 'Род'), (21, 'Подрод'), (22, 'Секция'), (23, 'Подсекция'),
    (24, 'Грекс'), (25, 'Естественный гибрид'), (26, 'Вид'), (27, 'Разновидность'),
    (28, 'Подвид'), (29, 'Без ранга'),
)

# Managers
class NaturalKeyManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class NaturalKeyTaxonsManager(models.Manager):
    def get_by_natural_key(self, order,name):
        return self.get(order=order,name=name)

# Create your models here.
class Categories(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name='Наименование')
    name_lower = models.CharField(max_length=255, unique=True, null=True, editable=False)
    slug=models.SlugField(max_length=255,unique=True,db_index=True,verbose_name='URL')
    time_create = models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True,verbose_name='Дата изменения')

    objects = NaturalKeyManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug=slugify(self.name)
        self.name_lower=self.name.lower()
        super(Categories, self).save(*args, **kwargs)

    class Meta:
        verbose_name="Категория"
        verbose_name_plural="Категории"
        ordering=['name']

class Taxons(models.Model):
    name = models.CharField(max_length=255,verbose_name='Наименование')
    slug=models.SlugField(max_length=255,unique=True,db_index=True,verbose_name='URL')
    order=models.IntegerField(default=0, choices=PRIORITIES, verbose_name='Ранг')
    time_create = models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True,verbose_name='Дата изменения')

    objects = NaturalKeyTaxonsManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug=slugify(self.name+'-'+self.get_order_display())
        super(Taxons, self).save(*args, **kwargs)

    class Meta:
        verbose_name="Таксон"
        verbose_name_plural="Таксоны"
        ordering=['name']
        unique_together=['order','name']


def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.name, ext)
    return os.path.join('plants/plants_image', filename)

class Plants(models.Model):
    name=models.CharField(max_length=255,unique=True,verbose_name='Название')
    name_lower=models.CharField(max_length=255,unique=True,null=True,editable=False)
    slug=models.SlugField(max_length=255,unique=True,db_index=True,editable=False,verbose_name='URL')
    image=models.ImageField(upload_to=content_file_name,blank=True)
    time_create=models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update=models.DateTimeField(auto_now=True,verbose_name='Дата изменения')
    categories=models.ManyToManyField(Categories,blank=True,verbose_name='Категории')
    taxons=models.ManyToManyField(Taxons,blank=True,verbose_name='Таксоны')

    objects = NaturalKeyManager()


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plant', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        self.slug=slugify(self.name)
        self.name_lower=self.name.lower()
        super(Plants, self).save(*args, **kwargs)

    class Meta:
        verbose_name="Растение"
        verbose_name_plural="Растения"
        ordering=['name']

class Descriptions(models.Model):
    category=models.CharField(max_length=64,verbose_name='Категория',blank=True)
    text=models.TextField(blank=True,verbose_name='Описание')
    time_create=models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update=models.DateTimeField(auto_now=True,verbose_name='Дата изменения')
    plant=models.ForeignKey(Plants,on_delete=models.CASCADE,verbose_name='Растение')

    def __str__(self):
        return self.plant.name+' '+self.category

    class Meta:
        verbose_name="Описание"
        verbose_name_plural="Описания"
        ordering=['category']