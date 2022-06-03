import os

from django.db import models
from django.shortcuts import reverse
from django.utils.translation import  gettext_lazy as _
from slugify import slugify


# TODO Create a model to store this information
PRIORITIES = (
    (0, _('Domain')), (1, _('Supra-kingdom')), (2, _('Kingdom')), (3, _('Sub-kingdom')), (4, _('Clade')),
    (5, _('Supra-department')), (6, _('Department')), (7, _('Sub-department')), (8, _('Superclass')), (9, _('Class')),
    (10, _('Subclass')), (11, _('Superorder')), (12, _('Order')), (13, _('Series ')), (14, _('Type')),
    (15, _('Family')), (16, _('Subfamily')), (17, _('Supertribe')), (18, _('Tribe')),
    (19, _('Subtribe')), (20, _('Genus')), (21, _('Subgenus')), (22, _('Section')), (23, _('Subsection')),
    (24, _('Grex')), (25, _('Natural hybrid')), (26, _('Kind')), (27, _('Variety')),
    (28, _('Subkind')), (29, _('Without rank')),
)


class NaturalKeyManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class NaturalKeyTaxonsManager(models.Manager):
    def get_by_natural_key(self, order,name):
        return self.get(order=order, name=name)


class Categories(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name=_('name'))
    name_lower = models.CharField(max_length=200, unique=True, null=True, editable=False)
    slug = models.SlugField(max_length=200, unique=True, db_index=True, editable=False, verbose_name='URL')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_('time create'))
    time_update = models.DateTimeField(auto_now=True, verbose_name=_('time update'))

    objects = NaturalKeyManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.name_lower = self.name.lower()
        super(Categories, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ('name',)


class Taxons(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    slug = models.SlugField(max_length=100, unique=True, db_index=True,
                            editable=False, verbose_name='URL')
    order = models.IntegerField(default=0, choices=PRIORITIES, verbose_name=_('rank'))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_('time create'))
    time_update = models.DateTimeField(auto_now=True, verbose_name=_('time update'))

    objects = NaturalKeyTaxonsManager()

    def __str__(self):
        return f'{self.get_order_display()}-{self.name}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name+'-'+self.get_order_display())
        super(Taxons, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("taxon")
        verbose_name_plural = _("taxons")
        ordering = ('name',)
        unique_together = (('order','name'),)


def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.name, ext)
    return os.path.join('plants/plants_image', filename)

class Plants(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('name'))
    name_lower = models.CharField(max_length=100, unique=True, null=True, editable=False)
    slug = models.SlugField(max_length=100, unique=True, db_index=True,
                            editable=False, verbose_name='URL')
    image = models.ImageField(upload_to=content_file_name, blank=True, verbose_name=_('image'))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_('time create'))
    time_update = models.DateTimeField(auto_now=True, verbose_name=_('time update'))
    categories = models.ManyToManyField(Categories, blank=True, verbose_name=_('categories'))
    taxons = models.ManyToManyField(Taxons, blank=True, verbose_name=_('taxons'))

    objects = NaturalKeyManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plant', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.name_lower = self.name.lower()
        super(Plants, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("plant")
        verbose_name_plural = _("plants")
        ordering = ('name',)


class Descriptions(models.Model):
    category = models.CharField(max_length=100, verbose_name=_('category'), blank=True)
    text = models.TextField(blank=True, verbose_name=_('description'))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_('time create'))
    time_update = models.DateTimeField(auto_now=True, verbose_name=_('time update'))
    plant = models.ForeignKey(Plants, on_delete=models.CASCADE, verbose_name=_('plant'))

    def __str__(self):
        return f'{self.plant.name} {self.category}'

    class Meta:
        verbose_name = _("description")
        verbose_name_plural = _("descriptions")
        ordering = ('category',)
        unique_together = (('plant','category'),)
