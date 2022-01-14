from django import template

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