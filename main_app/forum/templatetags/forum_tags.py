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


@register.inclusion_tag('forum/posts_form.html',takes_context=True)
def get_create_post_form(context, topic):
    return {'form': context['form'], 'topic':topic}


@register.simple_tag()
def get_post_score(post,scores):
    return scores[post]['score']


@register.simple_tag(takes_context=True)
def get_rate_form_with_initial_data(context,post,scores):
    form=context['rate_form'](initial={'value':scores[post]['rate']})
    return form.as_p()


@register.simple_tag()
def get_filename_from_path(path):
    path=path.__str__()
    return path.split('/')[-1]