from django.test import TestCase
from django.urls import reverse

from plants.models import *


class RandomPlantViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Plants.objects.create(name="Test plant")

    def test_view_redirect(self):
        response = self.client.get(reverse('random_plant'))
        self.assertEqual(response.status_code, 302)


class PlantsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_plant = 50
        cat = Categories.objects.create(name='cat')
        tax = Taxons.objects.create(name='taxon', order=0)
        for num_plant in range(number_of_plant):
            plant=Plants.objects.create(name=f'Plant_number_{num_plant}')
            plant.categories.add(cat)
            plant.taxons.add(tax)
            plant.save()

    def test_view_url_exists(self):
        response = self.client.get(reverse('plants'))
        self.assertEqual(response.status_code, 200)

    def test_view_response_code_with_existing_get_parameter(self):
        response = self.client.get(reverse('plants'), {'cat': 'cat', 'taxon': 'tax'})
        self.assertEqual(response.status_code, 200)

    def test_view_response_code_without_existing_get_parameter(self):
        response = self.client.get(reverse('plants'), {'cat': '123', 'taxon': '123'})
        self.assertEqual(response.status_code, 404)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('plants'))
        self.assertTemplateUsed(response, 'plants/plants_list.html')

    def test_model_used(self):
        response = self.client.get(reverse('plants'))
        object_list = response.context['object_list']
        self.assertEqual(object_list[0].__str__(), Plants.objects.get(pk=1).__str__())

    def test_pagination(self):
        response = self.client.get(reverse('plants'))

        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue( len(response.context['plants_list']) == 20)

    def test_context(self):
        response = self.client.get(reverse('plants'))
        self.assertTrue('title' in response.context)
        self.assertTrue('super_title' in response.context)
        self.assertTrue('super_url' in response.context)

    def test_filter_form(self):
        response = self.client.get(reverse('plants'))
        self.assertTrue('filter_form' in response.context)


class CategoriesListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_categories = 50
        for num_cat in range(number_of_categories):
            Categories.objects.create(name=f'cat{num_cat}')

    def test_view_url_exists(self):
        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('categories'))
        self.assertTemplateUsed(response, 'plants/categories_list.html')

    def test_model_used(self):
        response = self.client.get(reverse('categories'))
        object_list = response.context['object_list']
        self.assertEqual(object_list[0].__str__(),Categories.objects.get(pk=1).__str__())

    def test_pagination(self):
        response = self.client.get(reverse('categories'))

        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue( len(response.context['categories_list']) == 20)

    def test_context(self):
        response = self.client.get(reverse('plants'))
        self.assertTrue('title' in response.context)
        self.assertTrue('super_title' in response.context)
        self.assertTrue('super_url' in response.context)

    def test_filter_form(self):
        response = self.client.get(reverse('categories'))
        self.assertTrue('filter_form' in response.context)


class TaxonsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_taxons = 50
        for num_tax in range(number_of_taxons):
            Taxons.objects.create(name=f'tax{num_tax}', order=0)

    def test_view_url_exists(self):
        response = self.client.get(reverse('taxons_rang', kwargs={'id_rang': 0}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('taxons_rang', kwargs={'id_rang': 0}))
        self.assertTemplateUsed(response, 'plants/taxons_list.html')

    def test_model_used(self):
        response = self.client.get(reverse('taxons_rang', kwargs={'id_rang': 0}))
        object_list = response.context['object_list']
        self.assertEqual(object_list[0].__str__(),Taxons.objects.get(pk=1).__str__())

    def test_pagination(self):
        response = self.client.get(reverse('taxons_rang', kwargs={'id_rang': 0}))

        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue( len(response.context['taxons_list']) == 20)

    def test_context(self):
        response = self.client.get(reverse('taxons_rang',kwargs={'id_rang': 0}))
        self.assertTrue('title' in response.context)
        self.assertTrue('super_title' in response.context)
        self.assertTrue('super_url' in response.context)

    def test_search_non_existent_taxon(self):
        response = self.client.get(reverse('taxons_rang', kwargs={'id_rang': 500}))
        self.assertEqual(response.status_code, 404)

    def test_raise_404_title(self):
        response = self.client.get(reverse('taxons_rang', kwargs={'id_rang': 1}))
        self.assertEqual(response.status_code, 404)


class PlantDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Plants.objects.create(name='Plant')

    def test_view_url_exists(self):
        response = self.client.get(reverse('plant',kwargs={'slug': Plants.objects.get(pk=1).slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_search_non_existent_plant(self):
        response = self.client.get(reverse('plant', kwargs={'slug': '123'}))
        self.assertEqual(response.status_code, 404)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('plant',kwargs={'slug': Plants.objects.get(pk=1).slug}))
        self.assertTemplateUsed(response, 'plants/plants_detail.html')

    def test_model_used(self):
        response = self.client.get(reverse('plant',kwargs={'slug': Plants.objects.get(pk=1).slug}))
        object = response.context['object']
        self.assertEqual(object.__str__(),Plants.objects.get(pk=1).__str__())


class TaxonsRangViewTest(TestCase):
    def test_view_url_exists(self):
        response = self.client.get(reverse('taxons'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('taxons'))
        self.assertTemplateUsed(response, 'plants/taxons_rangs.html')

    def test_context(self):
        response = self.client.get(reverse('taxons'))
        self.assertTrue('title' in response.context)
        self.assertTrue('rangs' in response.context)
