from django.test import TestCase
from django.test import Client

from django.template.loader import render_to_string
from django.template import Context, Template

from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.core.files.base import ContentFile

from unittest import skip

from forum.models import *
from forum.forms import CreateTopicForm

from time import sleep

class BaseTemplateTest(TestCase):
    def setUp(self):
        template_name = 'forum/base.html'
        self.rendered_template = render_to_string(template_name)

    def test_icon_in_template(self):
        icon = '<link rel="shortcut icon" href="/static/forum/images/forum_icon.svg" ' \
               'type="image/x-icon">'
        self.assertInHTML(icon, self.rendered_template)

    def test_extrastyles_in_template(self):
        extra_styles = '<link type="text/css" href="/static/forum/css/forum.css" rel="stylesheet">'
        self.assertInHTML(extra_styles, self.rendered_template)

    def test_menu_app_in_template(self):
        menu_app = '<ul class="horizontal_menu">' \
                   '<li><a href="/forum/" class="app_menu_link">Главные разделы</a></li>' \
                   '<li><a href="/forum/topics" class="app_menu_link">Все темы</a></li>' \
                   '<li><a href="/forum/random" class="app_menu_link">Случайная тема</a></li>' \
                   '</ul>'
        self.assertInHTML(menu_app, self.rendered_template)


class DefaultFormPageTemplateTest(TestCase):
    def setUp(self):
        template_name = 'forum/default_form_page.html'
        self.rendered_template = render_to_string(template_name, {'form': CreateTopicForm()})

    def test_menu_app_in_template(self):
        menu_app = '<ul class="horizontal_menu">' \
                   '<li><a href="/forum/" class="app_menu_link">Главные разделы</a></li>' \
                   '<li><a href="/forum/topics" class="app_menu_link">Все темы</a></li>' \
                   '<li><a href="/forum/random" class="app_menu_link">Случайная тема</a></li>' \
                   '</ul>'
        self.assertInHTML(menu_app, self.rendered_template)


class MenuForumTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Sections.objects.create(name='Test Section')

    def setUp(self):
        self.template_name = 'forum/base.html'
        self.section = Sections.objects.get(pk=1)

    def test_menu_app_without_super_section(self):
        rendered_template = render_to_string(self.template_name)
        menu_app = '<ul class="horizontal_menu">' \
                   '<li><a href="/forum/" class="app_menu_link">Главные разделы</a></li>' \
                   '<li><a href="/forum/topics" class="app_menu_link">Все темы</a></li>' \
                   '<li><a href="/forum/random" class="app_menu_link">Случайная тема</a></li>' \
                   '</ul>'
        self.assertInHTML(menu_app, rendered_template)

    def test_menu_app_with_super_section(self):
        rendered_template = render_to_string(self.template_name,
                                             {'super_section': self.section})
        menu_app = '<ul class="horizontal_menu">' \
                   '<li><a href="/forum/" class="app_menu_link">Главные разделы</a></li>'\
                   '<li><a href="/forum/section/test-section" class="app_menu_link">Test Section</a></li>'\
                   '<li><a href="/forum/topics" class="app_menu_link">Все темы</a></li>' \
                   '<li><a href="/forum/random" class="app_menu_link">Случайная тема</a></li>' \
                   '</ul>'
        self.assertInHTML(menu_app, rendered_template)


class SuperSectionsListTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Sections.objects.create(name='Test Section')

    def setUp(self):
        template_name = 'forum/super_sections_list.html'
        self.rendered_template = render_to_string(template_name,
                                                  {'object_list': Sections.objects.all()})

    def test_has_table_sections(self):
        table = '<table>' \
                '<tr><td><p class="title">' \
                '<span class="number">1</span>' \
                '<a href="/forum/section/test-section" class="menu_link">Test Section</a>' \
                '</p></td></tr>' \
                '</table>'
        self.assertInHTML(table, self.rendered_template)


class TopicDetailTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)
        section = Sections.objects.create(name='Test Section')
        topic = Topics(name='Test topic', author=forum_user, sections=section)
        topic.save()
        post = Posts(author=forum_user, topic=topic, text="Test message", post_type=0)
        post.save()

    def setUp(self):
        self.topic = Topics.objects.get(pk=1)
        self.post = Posts.objects.get(topic=self.topic, post_type=0)
        self.forum_user = ForumUsers.objects.get(pk=1)

    def test_has_topic_title(self):
        title = f'<h2 class="super-title">{self.topic.name}</h2>'
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertContains(response, title)

    def test_has_pagination(self):
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        pagination = render_to_string('main_app/pagination.html',
                                      {'page_obj': response.context['page_obj']})
        self.assertContains(response, pagination)

    def test_can_delete_edit_topic(self):
        can_delete_topic = '<div class="topic-deleting">'
        # not auth user
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertNotContains(response, can_delete_topic)

        # auth user
        user = User.objects.create_user(username='User with permission', password='321ewq+.')
        permission = Permission.objects.get(codename='delete_topics')
        user.user_permissions.add(permission)

        permission = Permission.objects.get(codename='change_topics')
        user.user_permissions.add(permission)

        client = Client()
        client.login(username='User with permission', password='321ewq+.')
        response = client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertContains(response, can_delete_topic)

    def test_form_create_post(self):
        message = '<h3>Только зарегестрированные пользователи могут оставлять сообщения.</h3>'
        # not auth user
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertContains(response, message)

        # auth user
        user = User.objects.create_user(username='User with permission', password='321ewq+.')
        client = Client()
        client.login(username='User with permission', password='321ewq+.')
        response = client.get(reverse('topic', kwargs={'slug': self.topic.slug}))

        form = '<form action="{{action}}" enctype="{{enctype}}" method="post">'
        context = Context(response.context)
        form = Template(form).render(context)
        self.assertContains(response, form)

    def test_can_delete_post(self):
        post = Posts.objects.create(topic=self.topic, author=self.forum_user,
                                    text="test", post_type=1)
        can_delete_post = '<a href="{% url \'delete_post\' post.pk %}" class="app_link">'
        can_delete_post = Template(can_delete_post).render(Context({'post': post}))
        # not auth user
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertNotContains(response, can_delete_post)

        # auth user
        user = User.objects.create_user(username='User with permission', password='321ewq+.')
        permission = Permission.objects.get(codename='delete_posts')
        user.user_permissions.add(permission)

        client = Client()
        client.login(username='User with permission', password='321ewq+.')
        response = client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertContains(response, can_delete_post)

    def test_form_rate_post(self):
        form_rate = '<form action="{% url \'rate_post\' post.pk %}'
        # not auth user
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        context = Context({'post': self.post})
        form_rate = Template(form_rate).render(context)
        self.assertNotContains(response, form_rate)

        # auth user
        user = User.objects.create_user(username='User with permission', password='321ewq+.')
        client = Client()
        client.login(username='User with permission', password='321ewq+.')
        response = client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertContains(response, form_rate)

    @skip
    def test_changed_post_rate(self):
        # total post rate changes when user change his rate
        self.assertTrue(False)

    @skip
    def test_initial_rate_post(self):
        # show previous user rate post
        self.assertTrue(False)

    def test_attached_files(self):
        attached_files = '<div class="attached-files">'
        # does not have attached files
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertNotContains(response, attached_files)

        # have attached files
        post = Posts.objects.create(topic=self.topic, author=self.forum_user,
                                    text="test", post_type=1)
        AttachedFiles.objects.create(post=post,
                                     file=ContentFile(b'File', name=f'file.txt'))
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertContains(response, attached_files)

    def test_load_text_files(self):
        text_file = '<a href="{{file.get_absolute_url}}" download=""'
        post = Posts.objects.create(topic=self.topic, author=self.forum_user,
                                    text="test", post_type=1)
        file = AttachedFiles.objects.create(post=post,
                                     file=ContentFile(b'File', name=f'file.txt'))
        context = Context({'file': file})
        text_file = Template(text_file).render(context)
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertContains(response, text_file)

    def test_display_image_files(self):
        image_file = '<img src="{{file.get_absolute_url}}"'
        post = Posts.objects.create(topic=self.topic, author=self.forum_user,
                                    text="test", post_type=1)
        file = AttachedFiles.objects.create(post=post,
                                            file=ContentFile(b'File', name=f'file.png'))
        context = Context({'file': file})
        image_file = Template(image_file).render(context)
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertContains(response, image_file)


class TopicsListTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)
        section = Sections.objects.create(name='Test Section')
        topic = Topics(sections=section, name='Test topic', author=forum_user)
        topic.save()

    def setUp(self):
        self.section = Sections.objects.get(pk=1)

    def test_has_topic_title(self):
        title = '<a href="" class="super-title">'
        # detail section
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        self.assertContains(response, title)

        # all topics
        response = self.client.get(reverse('all_topics'))
        self.assertContains(response, title)

    def test_form_filter(self):
        # detail section
        form_filter = '<form action="{% url \'topics\' object.slug %}" method="get">'
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        context = Context(response.context)
        form_filter = Template(form_filter).render(context)
        self.assertContains(response, form_filter)

        # all topics
        form_filter = '<form action="{% url \'all_topics\' %}" method="get">'
        response = self.client.get(reverse('all_topics'))
        context = Context()
        form_filter = Template(form_filter).render(context)
        self.assertContains(response, form_filter)

    def test_create_topic(self):
        create_post = '<a href="{% url \'create_topic\' object.slug %}" class="app_link">'
        context = Context({'object': self.section})
        create_post = Template(create_post).render(context)
        # detail section
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        self.assertContains(response, create_post)

        # all topics
        response = self.client.get(reverse('all_topics'))
        self.assertNotContains(response, create_post)

    def test_have_sections(self):
        sections = '<p class="title sections-list">'
        # don't have
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        self.assertNotContains(response, sections)

        # have
        sections = Sections.objects.create(super_sections=self.section, name="Second Section")
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        self.assertContains(response, sections)

    def test_have_topics(self):
        topics = '<p class="title topics-list">'
        # have
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        self.assertContains(response, topics)

        # don't have
        section = Sections.objects.create(super_sections=self.section, name="Second Section")
        response = self.client.get(reverse('topics', kwargs={'slug': section.slug}))
        self.assertNotContains(response, topics)


class UpdatePostFormTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)
        section = Sections.objects.create(name='Test Section')
        topic = Topics(name='Test topic', author=forum_user, sections=section)
        topic.save()
        post = Posts(author=forum_user, topic=topic, text="Test message", post_type=0)
        post.save()

    def setUp(self):
        self.post = Posts.objects.get(pk=1)

    def test_initial_files(self):
        client = Client()
        client.login(username='User', password='123qwe+.')
        delete_initial = '<input type="checkbox" name="delete_initial">'
        # don't have initial
        response = client.get(reverse('update_post', kwargs={'pk':self.post.pk}))
        self.assertNotContains(response, delete_initial)

        # have initial
        attached_file = AttachedFiles.objects.create(post=self.post,
                                                     file=ContentFile(b'File', name=f'file.txt'))
        response = client.get(reverse('update_post', kwargs={'pk': self.post.pk}))
        self.assertContains(response, delete_initial)
        file_url = f'a href="{attached_file.get_absolute_url()}">'
        self.assertContains(response, file_url)

    @skip
    def test_attached_files_errors(self):
        # don't have errors
        # have errors
        pass