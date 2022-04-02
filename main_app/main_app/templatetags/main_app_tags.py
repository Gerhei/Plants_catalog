from django import template
import os
import random
from django.utils.http import urlencode

register=template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)

@register.inclusion_tag('main_app/pagination.html',takes_context=True)
def get_pagination(context):
    return {'page_obj':context['page_obj'],'request':context['request']}


@register.inclusion_tag('main_app/header.html',takes_context=True)
def get_header(context):
    return {'request':context['request']}


@register.inclusion_tag('main_app/navigation.html',takes_context=True)
def get_navigation(context):
    menu = [
        {'title': 'Главная', 'url_name': 'main'},
        {'title': 'Каталог растений', 'url_name': 'plants'},
        {'title': 'Форум', 'url_name': 'forum'},
        {'title': 'Новости', 'url_name': 'news'}
    ]
    return {'request':context['request'],'menu':menu}


@register.simple_tag(takes_context=True)
def get_number(context,count):
    return count+(context['page_obj'].number-1)*context['page_obj'].paginator.per_page


@register.inclusion_tag('main_app/footer.html',takes_context=True)
def get_footer(context):
    return {'request':context['request']}


@register.simple_tag()
def get_random_background_image():
    images=[]
    for root, dirs, files in os.walk('main_app/static/main_app/images/header_backgrounds'):
        for name_file in files:
            images.append(name_file)
    return '/static/main_app/images/header_backgrounds/'+random.choice(images)


@register.simple_tag()
def get_file_extension(file):
    return str(file).split('.')[-1]


@register.simple_tag()
def get_filename_from_url(url):
    return url.split('/')[-1]