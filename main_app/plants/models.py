from django.db import models

# Create your models here.
class Categories(models.Model):
    name = models.CharField(max_length=64, unique=True,verbose_name='Наименование')
    time_create = models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True,verbose_name='Дата изменения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Категория"
        verbose_name_plural="Категории"
        ordering=['name']

class Taxons(models.Model):
    name = models.CharField(max_length=64, unique=True,verbose_name='Наименование')
    rang = models.CharField(max_length=64,verbose_name='Ранг')
    time_create = models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True,verbose_name='Дата изменения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Таксон"
        verbose_name_plural="Таксоны"
        ordering=['name']

class Plants(models.Model):
    name=models.CharField(max_length=64,unique=True,verbose_name='Название')
    image=models.ImageField(upload_to="./static",blank=True)
    time_create=models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update=models.DateTimeField(auto_now=True,verbose_name='Дата изменения')
    categories=models.ManyToManyField(Categories)
    taxons=models.ManyToManyField(Taxons)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Растение"
        verbose_name_plural="Растения"
        ordering=['name']

class Descriptions(models.Model):
    category=models.CharField(max_length=64,verbose_name='Категория')
    text=models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to="./static",blank=True)
    time_create=models.DateTimeField(auto_now_add=True,verbose_name='Дата создания')
    time_update=models.DateTimeField(auto_now=True,verbose_name='Дата изменения')
    plant=models.ForeignKey(Plants,on_delete=models.CASCADE,verbose_name='Растение')

    def __str__(self):
        return self.plant.name+' '+self.category

    class Meta:
        verbose_name="Описание"
        verbose_name_plural="Описания"
        ordering=['category']