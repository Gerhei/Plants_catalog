# Generated by Django 4.0.4 on 2022-06-04 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_alter_comments_text_alter_news_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='source_url',
            field=models.URLField(max_length=1000, unique=True, verbose_name='link to the source'),
        ),
    ]