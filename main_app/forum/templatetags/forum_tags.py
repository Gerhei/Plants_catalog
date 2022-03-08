from django import template

register=template.Library()

@register.inclusion_tag('forum/menu_forum.html',takes_context=True)
def get_menu_forum(context):
    menu = [{'title': 'Главные разделы', 'url_name': 'forum'}]
    if 'super_section' in context:
        section=context['super_section']
        if section:
            menu_link={'title': section.name, 'url_name': 'topics','slug':section.slug}
            menu.append(menu_link)

    menu+=[{'title': 'Все темы', 'url_name': 'all_topics'},
        {'title': 'Случайная тема', 'url_name': 'random_topic'}]
    return {'menu':menu}