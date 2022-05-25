from django import template
from django.utils.translation import gettext as _


register = template.Library()


@register.inclusion_tag('forum/menu_forum.html', takes_context=True)
def get_menu_forum(context):
    menu = [{'title': _('Main sections'), 'url_name': 'forum'}]
    if 'super_section' in context:
        section = context['super_section']
        if section:
            menu_link = {'title': section.name, 'url_name': 'topics', 'slug': section.slug}
            menu.append(menu_link)

    menu += [{'title': _('All topics'), 'url_name': 'all_topics'},
             {'title': _('Random topic'), 'url_name': 'random_topic'}]
    return {'menu': menu}


@register.inclusion_tag('forum/posts_form.html', takes_context=True)
def get_create_post_form(context, topic):
    return {'form': context['form'], 'topic': topic}


@register.simple_tag()
def get_total_post_rate(dict, post_id):
    try:
        value = dict[post_id]
    except KeyError:
        # this post has not been rated yet
        value = 0
    return value


@register.simple_tag(takes_context=True)
def get_rate_form_with_initial_data(context, post_id, post_rate_by_user):
    try:
        value = post_rate_by_user[post_id]
    except KeyError:
        # user has not rated this post yet
        value = 0

    form = context['rate_form'](initial = {'value': value})
    return form.as_p()
