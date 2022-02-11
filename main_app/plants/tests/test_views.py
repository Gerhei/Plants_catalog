from django.test import TestCase
from plants.views import *
from plants.models import *
from django.urls import reverse

class PlantsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_plant=50
        cat=Categories.objects.create(name='cat')
        tax=Taxons.objects.create(name='taxon',order=0)
        for num_plant in range(number_of_plant):
            plant=Plants.objects.create(name=f'Plant_number_{num_plant}')
            plant.categories.add(cat)
            plant.taxons.add(tax)
            plant.save()

    def test_view_url_exists(self):
        resp = self.client.get(reverse('plants'))
        self.assertEqual(resp.status_code, 200)

    def test_view_response_code_with_existing_get_parameter(self):
        resp = self.client.get(reverse('plants'),{'cat':'cat','taxon':'tax'})
        self.assertEqual(resp.status_code, 200)

    def test_view_response_code_without_existing_get_parameter(self):
        resp = self.client.get(reverse('plants'), {'cat': '123', 'taxon': '123'})
        self.assertEqual(resp.status_code, 404)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('plants'))
        self.assertTemplateUsed(resp, 'plants/plants_list.html')

    def test_model_used(self):
        resp = self.client.get(reverse('plants'))
        object_list=resp.context['object_list']
        self.assertEqual(object_list[0].__str__(),Plants.objects.get(pk=1).__str__())

    def test_pagination(self):
        resp = self.client.get(reverse('plants'))

        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['plants_list']) == 20)

    def test_context(self):
        resp = self.client.get(reverse('plants'))
        self.assertTrue('title' in resp.context)
        self.assertTrue('super_title' in resp.context)
        self.assertTrue('super_url' in resp.context)

    def test_filter_form(self):
        resp = self.client.get(reverse('plants'))
        self.assertTrue('filter_form' in resp.context)

class CategoriesListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_categories=50
        for num_cat in range(number_of_categories):
            Categories.objects.create(name=f'cat{num_cat}')

    def test_view_url_exists(self):
        resp = self.client.get(reverse('categories'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('categories'))
        self.assertTemplateUsed(resp, 'plants/categories_list.html')

    def test_model_used(self):
        resp = self.client.get(reverse('categories'))
        object_list=resp.context['object_list']
        self.assertEqual(object_list[0].__str__(),Categories.objects.get(pk=1).__str__())

    def test_pagination(self):
        resp = self.client.get(reverse('categories'))

        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['categories_list']) == 20)

    def test_context(self):
        resp = self.client.get(reverse('plants'))
        self.assertTrue('title' in resp.context)
        self.assertTrue('super_title' in resp.context)
        self.assertTrue('super_url' in resp.context)

    def test_filter_form(self):
        resp = self.client.get(reverse('categories'))
        self.assertTrue('filter_form' in resp.context)

class TaxonsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_taxons=50
        for num_tax in range(number_of_taxons):
            Taxons.objects.create(name=f'tax{num_tax}',order=0)

    def test_view_url_exists(self):
        resp = self.client.get(reverse('taxons_rang',kwargs={'id_rang': 0}))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('taxons_rang',kwargs={'id_rang': 0}))
        self.assertTemplateUsed(resp, 'plants/taxons_list.html')

    def test_model_used(self):
        resp = self.client.get(reverse('taxons_rang',kwargs={'id_rang': 0}))
        object_list=resp.context['object_list']
        self.assertEqual(object_list[0].__str__(),Taxons.objects.get(pk=1).__str__())

    def test_pagination(self):
        resp = self.client.get(reverse('taxons_rang',kwargs={'id_rang': 0}))

        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['taxons_list']) == 20)

    def test_context(self):
        resp = self.client.get(reverse('taxons_rang',kwargs={'id_rang': 0}))
        self.assertTrue('title' in resp.context)
        self.assertTrue('super_title' in resp.context)
        self.assertTrue('super_url' in resp.context)

    def test_search_non_existent_taxon(self):
        resp = self.client.get(reverse('taxons_rang', kwargs={'id_rang': 500}))
        self.assertEqual(resp.status_code, 404)


class PlantDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Plants.objects.create(name='Plant')

    def test_view_url_exists(self):
        resp = self.client.get(reverse('plant',kwargs={'slug':Plants.objects.get(pk=1).slug}))
        self.assertEqual(resp.status_code, 200)

    def test_view_search_non_existent_plant(self):
        resp = self.client.get(reverse('plant', kwargs={'slug': '123'}))
        self.assertEqual(resp.status_code, 404)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('plant',kwargs={'slug':Plants.objects.get(pk=1).slug}))
        self.assertTemplateUsed(resp, 'plants/plants_detail.html')

    def test_model_used(self):
        resp = self.client.get(reverse('plant',kwargs={'slug':Plants.objects.get(pk=1).slug}))
        object=resp.context['object']
        self.assertEqual(object.__str__(),Plants.objects.get(pk=1).__str__())

class RandomPlantViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Plants.objects.create(name='Plant')

    def test_view_url_redirect(self):
        resp = self.client.get(reverse('random_plant'))
        self.assertEqual(resp.status_code, 302)

class TaxonsRangViewTest(TestCase):
    def test_view_url_exists(self):
        resp = self.client.get(reverse('taxons'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('taxons'))
        self.assertTemplateUsed(resp, 'plants/taxons_rangs.html')

    def test_context(self):
        resp = self.client.get(reverse('taxons'))
        self.assertTrue('title' in resp.context)
        self.assertTrue('rangs' in resp.context)