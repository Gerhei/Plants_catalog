from datetime import datetime

from django.test import TestCase

from django.template.loader import render_to_string
from django.template import Context, Template
from django.contrib.auth.models import User

from news.models import *
from news.forms import *

from unittest import skip


class BaseTemplateTest(TestCase):
    def setUp(self):
        template_name = 'news/base.html'
        self.rendered_template = render_to_string(template_name)

    def test_icon_in_template(self):
        icon = '<link rel="shortcut icon" href="/static/news/images/news_icon.ico" ' \
               'type="image/x-icon">'
        self.assertInHTML(icon, self.rendered_template)

    def test_extrastyles_in_template(self):
        extra_styles = '<link type="text/css" href="/static/news/css/news.css" rel="stylesheet">'
        self.assertInHTML(extra_styles, self.rendered_template)


class NewsDetailTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        News.objects.create(title='Test news', publication_date=datetime.now(),
                            source_url='https://test-url.com', content='<div>Test text</div>')

    def setUp(self):
        template_name = 'news/news_detail.html'
        self.news = News.objects.get(pk=1)
        self.rendered_template = render_to_string(template_name,
                                                  {'object': self.news,
                                                  'form': CreateCommentForm()})

    def test_menu_app_in_template(self):
        menu_app = '<ul class="horizontal_menu">' \
                   '<li><a href="/news/" class="app_menu_link">Список новостей</a></li>' \
                   '<li><a href="/news/random" class="app_menu_link">Случайная новость</a></li>' \
                   '</ul>'
        self.assertInHTML(menu_app, self.rendered_template)

    def test_article_with_content_in_template(self):
        content = '<article>%s</article>' % self.news.content
        self.assertInHTML(content, self.rendered_template)

    def test_source_url_in_template(self):
        source_url = '<a class="app_link" href="%s">%s</a>' \
                     % (self.news.source_url, self.news.source_url)
        self.assertInHTML(source_url, self.rendered_template)

    def test_vertical_menu_in_template(self):
        vertical_menu = '<ul class="vertical_menu">' \
                        '<li><a href="#" title="Вернуться к началу" class="topbutton">^Наверх</a></li>' \
                        '<li><a href="#comments" class="topbutton">К комментариям</a></li>' \
                        '</ul>'
        self.assertInHTML(vertical_menu, self.rendered_template)

    def test_has_pagination(self):
        response = self.client.get(reverse('detailed_news', kwargs={'slug': self.news.slug}))
        pagination = render_to_string('main_app/pagination.html',
                                      {'page_obj': response.context['page_obj']})
        self.assertContains(response, pagination)


class NewsListTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        News.objects.create(title='Test news', publication_date=datetime.now(),
                            source_url='https://test-url.com', content='<div>Test text</div>')

    def setUp(self):
        template_name = 'news/news_list.html'
        self.rendered_template = render_to_string(template_name, {'object_list': News.objects.all()})

    def test_form_filter(self):
        form_filter = '<form action="{% url \'news\' %}" method="get">'
        response = self.client.get(reverse('news'))
        context = Context(response.context)
        form_filter = Template(form_filter).render(context)
        self.assertContains(response, form_filter)

    def test_vertical_menu(self):
        vertical_menu = '<ul class="vertical_menu">' \
                        '<li><a href="/news/random" class="app_link">Случайная новость</a></li>' \
                        '<li><a href="#" title="Вернуться к началу" class="topbutton">^Наверх</a></li>' \
                        '</ul>'
        self.assertInHTML(vertical_menu, self.rendered_template)
