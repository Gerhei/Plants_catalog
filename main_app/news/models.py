from django.db import models

from django.contrib.auth.models import User

from django.shortcuts import reverse

from slugify import slugify

import re
from tldextract import extract


class News(models.Model):
    title = models.CharField(max_length=60, verbose_name='Заголовок')
    # case-insensitive search for SQLite
    title_lower = models.CharField(max_length=60, editable=False)
    slug = models.SlugField(max_length=60, unique=True, db_index=True,
                            editable=False, verbose_name='Слаг')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    # date of publication of the news on the source site, and not on this
    publication_date = models.DateTimeField(verbose_name='Дата публикации')
    # published on this site
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано ли')
    source_url = models.URLField(unique=True, verbose_name='Ссылка на источник')
    # content in HTML
    content = models.TextField(max_length=None, verbose_name='Текст новости')

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
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ('-publication_date',)


class Comments(models.Model):
    # TODO convert to text field
    text = models.CharField(max_length=1000, verbose_name='Комментарий')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    news = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name='Новость')

    def __str__(self):
        return f'Комментарий №{self.pk}'

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ('time_create',)