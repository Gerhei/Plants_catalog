from django.test import TestCase

from news.forms import *


class FilterFormTest(TestCase):
    def setUp(self):
        self.form = FilterForm()

    def test_title_required(self):
        required = self.form.fields['title'].required
        self.assertEquals(required, False)

    def test_title_max_length(self):
        max_length = self.form.fields['title'].max_length
        self.assertEquals(max_length, 255)

    def test_publication_date_required(self):
        required = self.form.fields['publication_date'].required
        self.assertEquals(required, False)

    def test_publication_date_widget(self):
        widget = self.form.fields['publication_date'].widget
        self.assertEquals(widget.__class__, forms.SelectDateWidget(years=YEARS).__class__)

    def test_sort_required(self):
        required = self.form.fields['sort'].required
        self.assertEquals(required, False)

    def test_sort_choices(self):
        choices = self.form.fields['sort'].choices
        self.assertEquals(choices, order_by)

    def test_order_required(self):
        required = self.form.fields['order'].required
        self.assertEquals(required, False)

    def test_order_choices(self):
        choices = self.form.fields['order'].choices
        self.assertEquals(choices, order_choices)

    def test_page_required(self):
        required = self.form.fields['page'].required
        self.assertEquals(required, False)

    def test_page_min_value(self):
        min_value = self.form.fields['page'].min_value
        self.assertEquals(min_value, 1)


class CreateCommentFormTest(TestCase):
    def setUp(self):
        self.form = CreateCommentForm()

    def test_captcha_in_form(self):
        self.assertTrue('captcha' in self.form.fields)

        user = User.objects.create_user(username='test_user', password='123qwe+.')
        form = CreateCommentForm(user=user)
        self.assertFalse('captcha' in form.fields)
