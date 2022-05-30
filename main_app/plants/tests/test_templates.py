from django.test import TestCase
from django.template.loader import render_to_string
from django.template import Context, Template
from django.core.files.base import ContentFile

from plants.models import *


class CategoriesListTemplateTest(TestCase):
    def test_form_filter(self):
        Categories.objects.create(name='Test category')
        form_filter = '<form action="{% url \'categories\' %}" method="get">'
        form_filter = Template(form_filter).render(Context())
        response = self.client.get(reverse('categories'))
        self.assertContains(response, form_filter)

    def test_has_pagination(self):
        Categories.objects.create(name='Test category')
        pagination = '<div class="pagination">'
        response = self.client.get(reverse('categories'))
        self.assertContains(response, pagination)

    def test_empty_object_list(self):
        empty_page = '<h3 class="search-result">'
        response = self.client.get(reverse('categories'))
        self.assertContains(response, empty_page)


class PlantsDetailTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Plants.objects.create(name='Test plant')

    def setUp(self):
        self.plant = Plants.objects.get(pk=1)

    def test_extrastyles_in_template(self):
        extrastyles = '<link type="text/css" href="/static/plants/css/plant.css" rel="stylesheet"/>'
        response = self.client.get(reverse('plant', kwargs={'slug': self.plant.slug}))
        self.assertContains(response, extrastyles)

    def test_image_in_tempalte(self):
        self.plant.image = ContentFile(b'Image', 'Image.png')
        self.plant.save()
        image = f'<a href="{self.plant.image.url }">'
        response = self.client.get(reverse('plant', kwargs={'slug': self.plant.slug}))
        self.assertContains(response, image)


class PlantsListTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Plants.objects.create(name='Test plant')

    def setUp(self):
        self.plant = Plants.objects.get(pk=1)

    def test_extrastyles_in_template(self):
        extrastyles = '<link type="text/css" href="/static/plants/css/plant.css" rel="stylesheet"/>'
        response = self.client.get(reverse('plants'))
        self.assertContains(response, extrastyles)

    def test_form_filters(self):
        form_filter = '<form action="{% url \'plants\' %}" method="get">'
        form_filter = Template(form_filter).render(Context())
        response = self.client.get(reverse('plants'))
        self.assertContains(response, form_filter)

    def test_empty_object_list(self):
        self.plant.delete()
        empty_page = '<h3 class="search-result">'
        response = self.client.get(reverse('plants'))
        self.assertContains(response, empty_page)

    def test_has_pagination(self):
        pagination = '<div class="pagination">'
        response = self.client.get(reverse('plants'))
        self.assertContains(response, pagination)


class TaxonsListTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Taxons.objects.create(name="Test taxon")

    def test_has_pagination(self):
        pagination = '<div class="pagination">'
        response = self.client.get(reverse('taxons_rang', kwargs={'id_rang': 0}))
        self.assertContains(response, pagination)


class TaxonsRangsTemplateTest(TestCase):
    def test_title_in_template(self):
        title = '<h2 class="title">'
        response = self.client.get(reverse('taxons'))
        self.assertContains(response, title)
