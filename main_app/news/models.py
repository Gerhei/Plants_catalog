import re

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse
from slugify import slugify
from tldextract import extract


class News(models.Model):
    title = models.CharField(max_length=60, verbose_name=_('title'))
    # case-insensitive search for SQLite
    title_lower = models.CharField(max_length=60, editable=False)
    slug = models.SlugField(max_length=60, unique=True, db_index=True,
                            editable=False, verbose_name=_('slug'))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_('time create'))
    # date of publication of the news on the source site, and not on this
    publication_date = models.DateTimeField(verbose_name=_('publication date'))
    # published on this site
    is_published = models.BooleanField(default=True, verbose_name=_('is published'))
    source_url = models.URLField(unique=True, verbose_name=_('link to the source'))
    # content in HTML
    content = models.TextField(max_length=None, verbose_name=_('news content'))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('detailed_news', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(f'{self.get_source_site_domain()}-{self.title}')
        self.title_lower = self.title.lower()
        super(News, self).save(*args, **kwargs)

    def get_source_site_domain(self):
        subdomain, domain, suffix = extract(self.source_url)
        ignored = ["www", "web"]
        if not subdomain or subdomain.lower() in ignored:
            return domain
        pat = r"^(?:{})\.".format("|".join(ignored))
        return re.sub(pat, "", subdomain)

    class Meta:
        verbose_name = _("news")
        verbose_name_plural = _("news")
        ordering = ('-publication_date',)


class Comments(models.Model):
    text = models.CharField(max_length=1000, verbose_name=_('comment'))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_('time create'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('user'))
    news = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name=_('news'))

    def __str__(self):
        return '%s №%s' % (_('Comment'), self.pk)

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
        ordering = ('time_create',)
