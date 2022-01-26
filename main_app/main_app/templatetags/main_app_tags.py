from django import template
import os
import random

register=template.Library()

@register.inclusion_tag('main_app/menu.html')
def get_menu():
    menu = [
        {'title': 'Главная', 'url_name': 'main'},
        {'title': 'Каталог растений', 'url_name': 'plants'},
        {'title': 'Форум', 'url_name': 'forum'},
        {'title': 'Новости', 'url_name': 'news'}
    ]
    return {'menu':menu}

@register.simple_tag()
def get_random_background_image():
    images=[]
    for root, dirs, files in os.walk('main_app/static/main_app/images/header_backgrounds'):
        for name_file in files:
            images.append(name_file)
    return '/static/main_app/images/header_backgrounds/'+random.choice(images)