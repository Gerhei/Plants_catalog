from datetime import datetime

from django.test import TestCase
from django.test import Client

from news.models import *
from news.views import NewsDetailView


class RandomNewsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        News.objects.create(title='Test news', publication_date=datetime.now(),
                            source_url='https://test-url.com', content='<div>Test text</div>')

    def test_view_redirect(self):
        response = self.client.get(reverse('random_news'))
        self.assertEqual(response.status_code, 302)


class NewsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        News.objects.create(title='Test news', publication_date=datetime.now(),
                            source_url='https://test-url.com', content='<div>Test text</div>')

    def setUp(self):
        self.news = News.objects.get(pk=1)

    def test_view_url_exists(self):
        response = self.client.get(reverse('news'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('news'))
        self.assertTemplateUsed(response, 'news/news_list.html')

    def test_context(self):
        response = self.client.get(reverse('news'))
        context = response.context
        self.assertTrue('title' in context)
        self.assertTrue('filter_form' in context)

    def test_has_pagination(self):
        response = self.client.get(reverse('news'))
        context = response.context
        self.assertTrue('page_obj' in context)

    def test_work_filter_form(self):
        for i in range(5):
            News.objects.create(title=f'Test news {i}', publication_date=datetime.now(),
                            source_url=f'https://test-url-{i}.com', content='<div>Test text</div>')
        response = self.client.get(reverse('news'), {'title': 'News'})
        context = response.context
        self.assertQuerysetEqual(context['page_obj'],
                                 News.objects.filter(title_lower__icontains='News'.lower()))


    def test_filter_publication_date(self):
        for i in range(2010, 2022):
            News.objects.create(title=f'Test news {i}',
                                publication_date=datetime(i, 5, 18, 0, 19, 10),
                                source_url=f'https://test-url-{i}.com', content='<div>Test text</div>')
        response = self.client.get(reverse('news'), {'publication_date_year': 2022})
        context = response.context
        self.assertQuerysetEqual(context['page_obj'],
                                 News.objects.filter(publication_date__year=2022))


class NewsDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        News.objects.create(title='Test news', publication_date=datetime.now(),
                            source_url='https://test-url.com', content='<div>Test text</div>')

    def setUp(self):
        self.news = News.objects.get(pk=1)

    def test_view_url_exists(self):
        response = self.client.get(reverse('detailed_news', kwargs={'slug': self.news.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('detailed_news', kwargs={'slug': self.news.slug}))
        self.assertTemplateUsed(response, 'news/news_detail.html')

    def test_context(self):
        response = self.client.get(reverse('detailed_news', kwargs={'slug': self.news.slug}))
        context = response.context
        self.assertTrue('title' in context)
        self.assertTrue('action' in context)
        self.assertTrue('submit_value' in context)

    def test_has_pagination(self):
        response = self.client.get(reverse('detailed_news', kwargs={'slug': self.news.slug}))
        context = response.context
        self.assertTrue('page_obj' in context)

    def test_success_url(self):
        user = User.objects.create_user(username='User', password='123qwe+.')
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.post(reverse('detailed_news', kwargs={'slug': self.news.slug}),
                               data={'text': 'test message', 'news': self.news, 'user': user})
        success_url = f'{self.news.get_absolute_url()}?page=last#comments'
        self.assertRedirects(response, success_url)

    def test_display_comment_related_to_news(self):
        for i in range(5):
            Comments.objects.create(text='Test comment', news=self.news)
        view = NewsDetailView()
        view.object = self.news
        queryset = view.get_queryset()
        self.assertQuerysetEqual(queryset,
                                 Comments.objects.filter(news=self.news))

    def test_create_comment(self):
        user = User.objects.create_user(username='User', password='123qwe+.')
        client = Client()
        client.login(username='User', password='123qwe+.')
        response = client.post(reverse('detailed_news', kwargs={'slug': self.news.slug}),
                               data={'text': 'unique test comment', 'news': self.news, 'user': user})
        comment, created = Comments.objects.get_or_create(news=self.news, text='unique test comment')
        self.assertFalse(created)
