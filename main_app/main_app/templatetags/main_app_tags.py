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

@register.inclusion_tag('main_app/menu.html')
def get_menu():
    menu = [
        {'title': 'Главная', 'url_name': 'main'},
        {'title': 'Каталог растений', 'url_name': 'plants'},
        {'title': 'Форум', 'url_name': 'forum'},
        {'title': 'Новости', 'url_name': 'news'}
    ]
    return {'menu':menu}

@register.inclusion_tag('main_app/pagination.html',takes_context=True)
def get_pagination(context):
    return {'page_obj':context['page_obj'],'request':context['request']}

@register.simple_tag()
def get_random_background_image():
    images=[]
    for root, dirs, files in os.walk('main_app/static/main_app/images/header_backgrounds'):
        for name_file in files:
            images.append(name_file)
    return '/static/main_app/images/header_backgrounds/'+random.choice(images)