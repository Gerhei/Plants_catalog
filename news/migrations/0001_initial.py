# Generated by Django 4.0.4 on 2022-06-07 00:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(max_length=200, verbose_name='title')),
                ('title_lower', models.TextField(editable=False, max_length=200)),
                ('slug', models.SlugField(editable=False, max_length=200, unique=True, verbose_name='slug')),
                ('time_create', models.DateTimeField(auto_now_add=True, verbose_name='time create')),
                ('publication_date', models.DateTimeField(verbose_name='publication date')),
                ('is_published', models.BooleanField(default=True, verbose_name='is published')),
                ('source_url', models.URLField(max_length=1000, unique=True, verbose_name='link to the source')),
                ('content', models.TextField(verbose_name='news content')),
            ],
            options={
                'verbose_name': 'news',
                'verbose_name_plural': 'news',
                'ordering': ('-publication_date',),
            },
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=1000, verbose_name='comment')),
                ('time_create', models.DateTimeField(auto_now_add=True, verbose_name='time create')),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.news', verbose_name='news')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
                'ordering': ('time_create',),
            },
        ),
    ]
