from django.test import TestCase
from plants.forms import *


class FilterFormTest(TestCase):
    def test_name_required(self):
        form = FilterForm()
        required = form.fields['name'].required
        self.assertEquals(required, False)

    def test_sort_required(self):
        form = FilterForm()
        required = form.fields['sort'].required
        self.assertEquals(required, False)

    def test_sort_choices(self):
        form = FilterForm()
        choices = form.fields['sort'].choices
        self.assertEquals(choices, order_by)

    def test_order_required(self):
        form = FilterForm()
        required = form.fields['order'].required
        self.assertEquals(required, False)

    def test_order_choices(self):
        form = FilterForm()
        choices = form.fields['order'].choices
        self.assertEquals(choices, order_choices)

    def test_page_required(self):
        form = FilterForm()
        required = form.fields['page'].required
        self.assertEquals(required, False)

    def test_page_min_value(self):
        form = FilterForm()
        min_value = form.fields['page'].min_value
        self.assertEquals(min_value, 1)

    def test_fields_in_get_parameters(self):
        get_param = ['cat','taxon']
        form = FilterForm(get_param)
        self.assertEquals('cat' in form.fields, True)
        self.assertEquals('taxon' in form.fields, True)

    def test_cat_required(self):
        get_param = ['cat']
        form = FilterForm(get_param)
        required = form.fields['cat'].required
        self.assertEquals(required, False)

    def test_cat_widget(self):
        get_param = ['cat']
        form = FilterForm(get_param)
        widget = form.fields['cat'].widget
        self.assertEquals(type(widget), forms.HiddenInput)

    def test_taxon_required(self):
        get_param = ['taxon']
        form = FilterForm(get_param)
        required = form.fields['taxon'].required
        self.assertEquals(required, False)

    def test_taxon_widget(self):
        get_param = ['taxon']
        form = FilterForm(get_param)
        widget = form.fields['taxon'].widget
        self.assertEquals(type(widget), forms.HiddenInput)