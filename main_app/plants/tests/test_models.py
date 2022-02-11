from django.test import TestCase
from plants.models import *
from slugify import slugify

class PlantsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Plants.objects.create(name='Plant')

    def setUp(self):
        self.plant=Plants.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(self.plant.name, self.plant.__str__())

    def test_get_absolute_url(self):
        self.assertEquals(self.plant.get_absolute_url(), f'/plants/{self.plant.slug}')

    def test_name_unique(self):
        unique = self.plant._meta.get_field('name').unique
        self.assertEquals(unique, True)

    def test_name_lower_unique(self):
        unique = self.plant._meta.get_field('name_lower').unique
        self.assertEquals(unique, True)

    def test_name_lower_editable(self):
        editable = self.plant._meta.get_field('name_lower').editable
        self.assertEquals(editable, False)

    def test_correct_creation_name_lower(self):
        name_lower=self.plant.name_lower
        self.assertEquals(name_lower, self.plant.name.lower())

    def test_slug_unique(self):
        unique=self.plant._meta.get_field('slug').unique
        self.assertEquals(unique, True)

    def test_slug_editable(self):
        editable=self.plant._meta.get_field('slug').editable
        self.assertEquals(editable, False)

    def test_correct_creation_slug(self):
        slug = self.plant.slug
        self.assertEquals(slug, slugify(self.plant.name))


class CategoriesModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Categories.objects.create(name='Category')

    def setUp(self):
        self.category = Categories.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(self.category.name, self.category.__str__())

    def test_name_unique(self):
        unique = self.category._meta.get_field('name').unique
        self.assertEquals(unique, True)

    def test_name_lower_unique(self):
        unique = self.category._meta.get_field('name_lower').unique
        self.assertEquals(unique, True)

    def test_name_lower_editable(self):
        editable = self.category._meta.get_field('name_lower').editable
        self.assertEquals(editable, False)

    def test_correct_creation_name_lower(self):
        name_lower=self.category.name_lower
        self.assertEquals(name_lower, self.category.name.lower())

    def test_slug_unique(self):
        unique=self.category._meta.get_field('slug').unique
        self.assertEquals(unique, True)

    def test_correct_creation_slug(self):
        slug = self.category.slug
        self.assertEquals(slug, slugify(self.category.name))


class TaxonsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Taxons.objects.create(name='Taxon',order=0)

    def setUp(self):
        self.taxon = Taxons.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(self.taxon.name, self.taxon.__str__())

    def test_slug_unique(self):
        unique = self.taxon._meta.get_field('slug').unique
        self.assertEquals(unique, True)

    def test_correct_order_choices(self):
        choices=self.taxon._meta.get_field('order').choices
        self.assertEquals(choices,PRIORITIES)


class DescriptionsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        plant=Plants.objects.create(name='Plant')
        Descriptions.objects.create(category='Category',text='',plant=plant)

    def setUp(self):
        self.description = Descriptions.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(self.description.plant.name+' '+self.description.category,self.description.__str__())
