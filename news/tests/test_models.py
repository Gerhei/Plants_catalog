from datetime import datetime

from django.test import TestCase

from news.models import *


class NewsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        News.objects.create(title='Test news', publication_date=datetime.now(),
                            source_url='https://test-url.com', content='<div>Test text</div>')

    def setUp(self):
        self.news = News.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(self.news.title, self.news.__str__())

    def test_get_absolute_url(self):
        url = reverse('detailed_news', kwargs={'slug': self.news.slug})
        self.assertEquals(self.news.get_absolute_url(), url)

    def test_get_source_site_domain(self):
        site_name = self.news.get_source_site_domain()
        self.assertEquals(site_name, 'test-url')

    def test_ordering(self):
        ordering = self.news._meta.ordering
        self.assertEquals(ordering, ('-publication_date',))

    def test_correct_creation_slug(self):
        slug = self.news.slug
        self.assertEquals(slug, slugify(f'{self.news.get_source_site_domain()}-{self.news.title}'))

    def test_correct_creation_title_lower(self):
        title_lower = self.news.title_lower
        self.assertEquals(title_lower, self.news.title.lower())

    def test_title_max_length(self):
        max_length = self.news._meta.get_field('title').max_length
        self.assertEquals(max_length, 60)

    def test_title_lower_max_length(self):
        title_lower_max_length = self.news._meta.get_field('title_lower').max_length
        title_max_length = self.news._meta.get_field('title').max_length
        self.assertEquals(title_lower_max_length, title_max_length)

    def test_title_lower_editable(self):
        editable = self.news._meta.get_field('title_lower').editable
        self.assertEquals(editable, False)

    def test_slug_max_length(self):
        max_length = self.news._meta.get_field('slug').max_length
        self.assertEquals(max_length, 60)

    def test_slug_unique(self):
        unique = self.news._meta.get_field('slug').unique
        self.assertEquals(unique, True)

    def test_slug_editable(self):
        editable = self.news._meta.get_field('slug').editable
        self.assertEquals(editable, False)

    def test_time_create_auto_now_add(self):
        auto_now_add = self.news._meta.get_field('time_create').auto_now_add
        self.assertEquals(auto_now_add, True)

    def test_publication_date_field_exists(self):
        self.assertTrue(hasattr(self.news, 'publication_date'))

    def test_is_published_default(self):
        default = self.news._meta.get_field('is_published').default
        self.assertEquals(default, True)

    def test_source_url_unique(self):
        unique = self.news._meta.get_field('source_url').unique
        self.assertEquals(unique, True)

    def test_content_max_length(self):
        max_length = self.news._meta.get_field('content').max_length
        self.assertEquals(max_length, None)


class CommentsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        news = News.objects.create(title='Test news', publication_date=datetime.now(),
                                   source_url='https://test-url.com', content='<div>Test text</div>')
        Comments.objects.create(text='Test comment', news=news)

    def setUp(self):
        self.comment = Comments.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(f'Комментарий №{self.comment.pk}', self.comment.__str__())

    def test_ordering(self):
        ordering = self.comment._meta.ordering
        self.assertEquals(ordering, ('time_create',))

    def test_text_max_length(self):
        max_length = self.comment._meta.get_field('text').max_length
        self.assertEquals(max_length, 1000)

    def test_time_create_auto_now_add(self):
        auto_now_add = self.comment._meta.get_field('time_create').auto_now_add
        self.assertEquals(auto_now_add, True)

    def test_user_null(self):
        null = self.comment._meta.get_field('user').null
        self.assertEquals(null, True)

    def test_news_field_exists(self):
        self.assertTrue(hasattr(self.comment, 'news'))
