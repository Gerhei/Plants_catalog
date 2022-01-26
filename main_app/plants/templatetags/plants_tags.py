from django import template

register=template.Library()

@register.filter()
def sort_taxons(list):
    return list.order_by('order')