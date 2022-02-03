from django import template
from django.utils.http import urlencode

register=template.Library()

@register.filter()
def sort_taxons(list):
    return list.order_by('order')

@register.inclusion_tag('plants/menu_plant.html')
def get_menu_plant():
    menu = [
        {'title': 'Все растения', 'url_name': 'plants'},
        {'title': 'Категории', 'url_name': 'categories'},
        {'title': 'Таксоны', 'url_name': 'taxons'},
        {'title': 'Случайное растение', 'url_name': 'random_plant'}
    ]
    return {'menu':menu}

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)

@register.simple_tag(takes_context=True)
def get_number(context,count):
    return count+(context['page_obj'].number-1)*context['page_obj'].paginator.per_page