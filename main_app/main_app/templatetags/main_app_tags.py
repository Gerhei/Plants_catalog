from django import template
import os
import random
from django.utils.http import urlencode
from django.utils.translation import gettext as _


register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    try:
        query = context['request'].GET.dict()
    except KeyError:
        query = dict()
    query.update(kwargs)
    return urlencode(query)


@register.inclusion_tag('main_app/pagination.html',takes_context=True)
def get_pagination(context):
    try:
        page_obj = context['page_obj']
    except KeyError:
        page_obj = None

    try:
        request = context['request']
    except KeyError:
        request = None

    return {'page_obj': page_obj, 'request': request}


@register.inclusion_tag('main_app/header.html',takes_context=True)
def get_header(context):
    try:
        request = context['request']
    except KeyError:
        request = None

    return {'request': request}


@register.inclusion_tag('main_app/navigation.html', takes_context=True)
def get_navigation(context):
    menu = [
        {'title': _('About'), 'url_name': 'main'},
        {'title': _('Plant catalog'), 'url_name': 'plants'},
        {'title': _('Forum'), 'url_name': 'forum'},
        {'title': _('News'), 'url_name': 'news'}
    ]
    try:
        request = context['request']
    except KeyError:
        request = None

    return {'request': request, 'menu': menu}


@register.simple_tag(takes_context=True)
def get_number(context,count):
    return count + (context['page_obj'].number-1) * context['page_obj'].paginator.per_page


@register.inclusion_tag('main_app/footer.html',takes_context=True)
def get_footer(context):
    try:
        request = context['request']
    except KeyError:
        request = None
    return {'request': request}


@register.inclusion_tag('main_app/default_post_form.html', takes_context=True)
def get_default_form(context):
    return {'form': context['form']}


@register.simple_tag()
def get_random_background_image():
    images=[]
    for root, dirs, files in os.walk('main_app/static/main_app/images/header_backgrounds'):
        for name_file in files:
            images.append(name_file)
    return '/static/main_app/images/header_backgrounds/' + random.choice(images)


@register.simple_tag()
def get_file_extension(file):
    return str(file).split('.')[-1]


@register.simple_tag()
def get_filename_from_url(url):
    return url.split('/')[-1]
