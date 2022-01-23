from django.db import models

# Managers
class NaturalKeyManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class NaturalKeyTaxonsManager(models.Manager):
    def get_by_natural_key(self, rang,name):
        return self.get(rang=rang,name=name)

# Create your models here.
class Categories(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name='Наименование')
    slug=models.SlugField(max_length=255,unique=True,db_index=True,verbose_name='URL')
    time_create = models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True,verbose_name='Дата изменения')

    objects = NaturalKeyManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Категория"
        verbose_name_plural="Категории"
        ordering=['name']

class Taxons(models.Model):
    name = models.CharField(max_length=255,verbose_name='Наименование')
    slug=models.SlugField(max_length=255,unique=True,db_index=True,verbose_name='URL')
    rang = models.CharField(max_length=255,verbose_name='Ранг')
    time_create = models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True,verbose_name='Дата изменения')

    objects = NaturalKeyTaxonsManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Таксон"
        verbose_name_plural="Таксоны"
        ordering=['name']
        unique_together=['rang','name']

class Plants(models.Model):
    name=models.CharField(max_length=255,unique=True,verbose_name='Название')
    slug=models.SlugField(max_length=255,unique=True,db_index=True,verbose_name='URL')
    image=models.ImageField(upload_to="./static",blank=True)
    image_url=models.CharField(max_length=1024,blank=True)
    time_create=models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update=models.DateTimeField(auto_now=True,verbose_name='Дата изменения')
    categories=models.ManyToManyField(Categories,blank=True,verbose_name='Категории')
    taxons=models.ManyToManyField(Taxons,blank=True,verbose_name='Таксоны')

    objects = NaturalKeyManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Растение"
        verbose_name_plural="Растения"
        ordering=['name']

class Descriptions(models.Model):
    category=models.CharField(max_length=64,verbose_name='Категория',blank=True)
    text=models.TextField(verbose_name='Описание')
    time_create=models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update=models.DateTimeField(auto_now=True,verbose_name='Дата изменения')
    plant=models.ForeignKey(Plants,on_delete=models.CASCADE,verbose_name='Растение')

    def __str__(self):
        return self.plant.name+' '+self.category

    class Meta:
        verbose_name="Описание"
        verbose_name_plural="Описания"
        ordering=['category']