from datetime import timedelta, datetime

from django.contrib.sitemaps import Sitemap

from plants.models import Plants
from forum.models import Topics
from news.models import News


class PlantSitemap(Sitemap):
    changefreq = 'never'
    priority = 1.0

    def items(self):
        return Plants.objects.filter()

    def lastmod(self, obj):
        return obj.time_create


class ForumSitemap(Sitemap):
    changefreq = 'hourly'

    def items(self):
        return Topics.objects.filter()

    def lastmod(self, obj):
        return obj.time_create

    def priority(self, obj):
        if datetime.now() - obj.time_create <= timedelta(days=7):
            return 0.6
        else:
            return 0.4


class NewsSitemap(Sitemap):
    changefreq = 'daily'

    def items(self):
        return News.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.publication_date

    def priority(self, obj):
        if datetime.now() - obj.publication_date <= timedelta(days=7):
            return 0.8
        else:
            return 0.6
