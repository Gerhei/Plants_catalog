from django import template
from django.utils.translation import gettext as _


register=template.Library()


@register.filter()
def sort_taxons(list):
    return list.order_by('order')

@register.inclusion_tag('plants/menu_plant.html')
def get_menu_plant():
    menu = [
        {'title': _('All plants'), 'url_name': 'plants'},
        {'title': _('Categories'), 'url_name': 'categories'},
        {'title': _('Taxons'), 'url_name': 'taxons'},
        {'title': _('Random plant'), 'url_name': 'random_plant'}
    ]
    return {'menu': menu}
