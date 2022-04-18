from django.test import TestCase, TransactionTestCase, SimpleTestCase
from django.test import Client

from unittest import skip

from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.core.files.base import ContentFile

from forum.models import *

from time import sleep


class RandomTopicViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)

        section = Sections.objects.create(name='Раздел 1')
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()
        Posts.objects.create(author=forum_user, topic=topic, text="Test message", post_type=0)

    def test_view_redirect(self):
        response = self.client.get(reverse('random_topic'))
        self.assertEqual(response.status_code, 302)


class SectionsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Sections.objects.create(name='Main Section')

    def setUp(self):
        self.section = Sections.objects.get(pk=1)

    def test_view_url_exists(self):
        response = self.client.get(reverse('forum'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('forum'))
        self.assertTemplateUsed(response, 'forum/super_sections_list.html')

    def test_only_super_sections(self):
        Sections.objects.create(name="Second section", super_sections=self.section)
        response = self.client.get(reverse('forum'))
        object_list = response.context['object_list']
        for section in object_list:
            self.assertEqual(section.super_sections, None)

    def test_context(self):
        response = self.client.get(reverse('forum'))
        context = response.context
        self.assertTrue('title' in context)
        self.assertTrue('super_title' in context)


class TopicsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)

        section = Sections.objects.create(name='Раздел 1')
        topic = Topics(name='First topic', author=forum_user, sections=section)
        topic.save()

    def setUp(self):
        self.forum_user = ForumUsers.objects.get(pk=1)
        self.section = Sections.objects.get(pk=1)

    def test_view_url_exists(self):
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('all_topics'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        self.assertTemplateUsed(response, 'forum/topics_list.html')

        response = self.client.get(reverse('all_topics'))
        self.assertTemplateUsed(response, 'forum/topics_list.html')

    def test_context(self):
        Sections.objects.create(name="New", super_sections=self.section)
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        context = response.context
        self.assertTrue('title' in context)
        self.assertTrue('sections' in context)
        self.assertTrue('super_section' in context)
        self.assertTrue('filter_form' in context)

    def test_all_topics(self):
        response = self.client.get(reverse('all_topics'))
        context = response.context

        self.assertFalse('object' in context)
        self.assertFalse('sections' in context)
        self.assertFalse('super_section' in context)
        self.assertEqual(context['title'], "Все темы")

    def test_object_class(self):
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        context = response.context
        object = context['object']
        self.assertEqual(object.__class__, Sections)

    def test_has_pagination(self):
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        context = response.context
        self.assertTrue('page_obj' in context)

    def test_paginate_topics(self):
        response = self.client.get(reverse('topics', kwargs={'slug': self.section.slug}))
        context = response.context
        self.assertEqual(context['page_obj'][0].__class__, Topics)

    def test_count_topic_in_all_topics(self):
        for i in range(5):
            topic = Topics(name=f'Topic №{i}', author=self.forum_user, sections=self.section)
            topic.save()
        response = self.client.get(reverse('all_topics'))
        context = response.context
        all_topics = Topics.objects.all()
        self.assertCountEqual(all_topics, context['page_obj'])

    def test_work_filter_form(self):
        for i in range(5):
            topic = Topics(name=f'Topic №{i}', author=self.forum_user, sections=self.section)
            topic.save()
        response = self.client.get(reverse('all_topics'), {'name': 'First'})
        context = response.context
        self.assertQuerysetEqual(context['page_obj'],
                                 Topics.objects.filter(name_lower__icontains='First'))



class TopicDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)

        section = Sections.objects.create(name='Раздел 1')
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()
        post = Posts(author=forum_user, topic=topic, text="Test message", post_type=0)
        post.save()

    def setUp(self):
        self.topic = Topics.objects.get(pk=1)

    def test_view_url_exists(self):
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        self.assertTemplateUsed(response, 'forum/topic_detail.html')

    def test_context(self):
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        context = response.context
        self.assertTrue('title' in context)
        self.assertTrue('super_section' in context)
        self.assertTrue('can_delete_post' in context)
        self.assertTrue('can_delete_topic' in context)
        self.assertTrue('rate_form' in context)
        self.assertTrue('form' in context)
        self.assertTrue('submit_value' in context)
        self.assertTrue('enctype' in context)
        self.assertTrue('action' in context)

    def test_object_class(self):
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        context = response.context
        object = context['object']
        self.assertEqual(object.__class__, Topics)

    def test_has_pagination(self):
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        context = response.context
        self.assertTrue('page_obj' in context)

    def test_paginate_posts(self):
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        context = response.context
        self.assertEqual(context['page_obj'][0].__class__, Posts)

    def test_show_current_user_rate_post(self):
        client = Client()
        client.login(username='User', password='123qwe+.')
        response = client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        context = response.context
        self.assertTrue('post_rate_by_user' in context)

        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        context = response.context
        self.assertFalse('post_rate_by_user' in context)

    def test_increase_view_count_when_first_visit_auth_user(self):
        view_count = self.topic.view_count
        client = Client()
        client.login(username='User', password='123qwe+.')
        response = client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        after_view_count = Topics.objects.get(pk=self.topic.pk).view_count
        self.assertEqual(view_count + 1, after_view_count)

    def test_increase_view_count_when_second_visit_auth_user(self):
        client = Client()
        client.login(username='User', password='123qwe+.')
        response = client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        first_view_count = Topics.objects.get(pk=self.topic.pk).view_count

        response = client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        second_view_count = Topics.objects.get(pk=self.topic.pk).view_count

        self.assertEqual(first_view_count, second_view_count)

    def test_increase_view_count_when_visit_not_auth_user(self):
        view_count = self.topic.view_count
        response = self.client.get(reverse('topic', kwargs={'slug': self.topic.slug}))
        after_view_count = Topics.objects.get(pk=self.topic.pk).view_count
        self.assertEqual(view_count, after_view_count)



class PostCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)

        section = Sections.objects.create(name='Раздел 1')
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()

    def setUp(self):
        self.topic = Topics.objects.get(pk=1)
        self.forum_user = ForumUsers.objects.get(pk=1)

    def test_allowed_only_post(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.get(reverse('create_post', kwargs={'pk': self.topic.pk}))
        self.assertEqual(response.status_code, 405)

    def test_redirect_not_auth_user(self):
        response = self.client.post(reverse('create_post', kwargs={'pk': self.topic.pk}),
                                    data={'text': 'test_redirect_not_auth_user'})
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_post_created(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.post(reverse('create_post', kwargs={'pk': self.topic.pk}),
                               data={'text': 'test_post_created'})
        post, created = Posts.objects.get_or_create(topic=self.topic, text='test_post_created',
                                                    post_type=1, author=self.forum_user)
        self.assertFalse(created)

    def test_success_url(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.post(reverse('create_post', kwargs={'pk': self.topic.pk}),
                               data={'text': 'test message'})
        post = Posts.objects.filter(topic=self.topic).last()
        success_url = f'{self.topic.get_absolute_url()}?page=last#{post.pk}'
        self.assertRedirects(response, success_url)

    def test_create_attached_files(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        files = []
        num_created_files = 2
        for i in range(num_created_files):
            files.append(ContentFile(b'File', name=f'file {i}.txt'))


        response = client.post(reverse('create_post', kwargs={'pk': self.topic.pk}),
                               data={'text': 'test_create_attached_files',
                                     'attached_files': files})
        post, created = Posts.objects.get_or_create(topic=self.topic,
                                                    text='test_create_attached_files',
                                                    post_type=1, author=self.forum_user)
        self.assertFalse(created)
        attached_files = AttachedFiles.objects.filter(post=post)
        self.assertEqual(attached_files.count(), num_created_files)

    def test_not_attach_files_with_validation_errors(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        files = []
        num_created_files = 2
        for i in range(num_created_files):
            files.append(ContentFile(b'File', name=f'file {i}.exe'))

        response = client.post(reverse('create_post', kwargs={'pk': self.topic.pk}),
                               data={'text': 'test_create_attached_files',
                                     'attached_files': files})
        post, created = Posts.objects.get_or_create(topic=self.topic,
                                                    text='test_create_attached_files',
                                                    post_type=1, author=self.forum_user)
        self.assertFalse(created)
        attached_files = AttachedFiles.objects.filter(post=post)
        self.assertEqual(attached_files.count(), 0)


class TopicCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)

        section = Sections.objects.create(name='Раздел 1')

    def setUp(self):
        self.forum_user = ForumUsers.objects.get(pk=1)
        self.section = Sections.objects.get(pk=1)

    def test_view_uses_correct_template(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.get(reverse('create_topic', kwargs={'slug': self.section.slug}))
        self.assertTemplateUsed(response, 'forum/default_form_page.html')

    def test_context(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.get(reverse('create_topic', kwargs={'slug': self.section.slug}))
        context = response.context
        self.assertIn('title', context)
        self.assertIn('enctype', context)
        self.assertIn('submit_value', context)
        self.assertIn('change_text', context)

    def test_view_url_exists(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.get(reverse('create_topic', kwargs={'slug': self.section.slug}))
        self.assertEqual(response.status_code, 200)

    def test_redirect_not_auth_user(self):
        response = self.client.get(reverse('create_topic', kwargs={'slug': self.section.slug}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_success_url(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.post(reverse('create_topic', kwargs={'slug': self.section.slug}),
                               data={'text': 'test_success_url', 'name': 'test_success_url',
                                     'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'})
        topic = Topics.objects.get(name='test_success_url')
        self.assertRedirects(response, topic.get_absolute_url())

    def test_post_not_auth_user(self):
        response = self.client.post(reverse('create_topic', kwargs={'slug': self.section.slug}),
                               data={'text': 'test_success_url', 'name': 'test_success_url',
                                     'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'})
        self.assertEqual(response.status_code, 302)

    def test_topic_created(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.post(reverse('create_topic', kwargs={'slug': self.section.slug}),
                               data={'text': 'test_topic_created', 'name': 'test_topic_created',
                                     'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'})
        topic, created = Topics.objects.get_or_create(sections=self.section,
                                                      author=self.forum_user)
        self.assertFalse(created)

    def test_create_attached_files(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        files = []
        num_created_files = 2
        for i in range(num_created_files):
            files.append(ContentFile(b'File', name=f'file {i}.txt'))

        response = client.post(reverse('create_topic', kwargs={'slug': self.section.slug}),
                               data={'text': 'test_create_attached_files',
                                     'name': 'test_create_attached_files',
                                     'attached_files': files,
                                     'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'})
        topic, created = Topics.objects.get_or_create(sections=self.section,
                                                      name='test_create_attached_files',
                                                      author=self.forum_user)
        self.assertFalse(created)
        post = Posts.objects.get(topic=topic, post_type=0)
        attached_files = AttachedFiles.objects.filter(post=post)
        self.assertEqual(attached_files.count(), num_created_files)

    def test_not_attach_files_with_validation_errors(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        files = []
        num_created_files = 2
        for i in range(num_created_files):
            files.append(ContentFile(b'File', name=f'file {i}.exe'))

        response = client.post(reverse('create_topic', kwargs={'slug': self.section.slug}),
                               data={'text': 'test_create_attached_files',
                                     'name': 'test_create_attached_files',
                                     'attached_files': files,
                                     'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'})
        topic, created = Topics.objects.get_or_create(sections=self.section,
                                                      name='test_create_attached_files',
                                                      author=self.forum_user)
        self.assertFalse(created)
        post = Posts.objects.get(topic=topic, post_type=0)
        attached_files = AttachedFiles.objects.filter(post=post)
        self.assertEqual(attached_files.count(), 0)


class PostUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)

        section = Sections.objects.create(name='Раздел 1')
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()
        Posts.objects.create(author=forum_user, topic=topic, text="Test message", post_type=0)

    def setUp(self):
        self.forum_user = ForumUsers.objects.get(pk=1)
        self.post = Posts.objects.get(pk=1)

    def test_view_uses_correct_template(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.get(reverse('update_post', kwargs={'pk': self.post.pk}))
        self.assertTemplateUsed(response, 'forum/update_post_form.html')

    def test_context(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.get(reverse('update_post', kwargs={'pk': self.post.pk}))
        context = response.context
        self.assertIn('title', context)
        self.assertIn('attached_files_errors', context)
        self.assertIn('initial_files', context)
        self.assertIn('submit_value', context)
        self.assertIn('enctype', context)
        self.assertIn('change_text', context)

    def test_view_url_exists(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.get(reverse('update_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_redirect_not_auth_user(self):
        response = self.client.get(reverse('update_post', kwargs={'pk': self.post.pk}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_success_url(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.post(reverse('update_post', kwargs={'pk': self.post.pk}),
                               data={'text': 'test_success_url'})
        self.assertRedirects(response, f'{self.post.topic.get_absolute_url()}'
                                       f'?page=last#{self.post.pk}')

    def test_post_not_auth_user(self):
        response = self.client.post(reverse('update_post', kwargs={'pk': self.post.pk}),
                               data={'text': 'test_post_not_auth_user'})
        self.assertEqual(response.status_code, 302)

    def test_post_changed(self):
        client = Client()
        client.login(username='User', password='123qwe+.')
        sleep(1)
        response = client.post(reverse('update_post', kwargs={'pk': self.post.pk}),
                               data={'text': 'test_post_changed'})
        post = Posts.objects.get(pk=self.post.pk)
        self.assertTrue(post.is_changed())

    def test_create_attached_files(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        files = []
        num_created_files = 2
        for i in range(num_created_files):
            files.append(ContentFile(b'File', name=f'file {i}.txt'))

        response = client.post(reverse('update_post', kwargs={'pk': self.post.pk}),
                               data={'text': 'test_create_attached_files',
                                     'attached_files': files})

        attached_files = AttachedFiles.objects.filter(post=self.post)
        self.assertEqual(attached_files.count(), num_created_files)

    def test_not_attach_files_with_validation_errors(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        files = []
        num_created_files = 2
        for i in range(num_created_files):
            files.append(ContentFile(b'File', name=f'file {i}.exe'))

        response = client.post(reverse('update_post', kwargs={'pk': self.post.pk}),
                               data={'text': 'test_create_attached_files',
                                     'attached_files': files})
        attached_files = AttachedFiles.objects.filter(post=self.post)
        self.assertEqual(attached_files.count(), 0)

    def test_dont_delete_initial_files(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        num_initial_files = 2
        for i in range(num_initial_files):
            file = ContentFile(b'File', name=f'file {i}.txt')
            AttachedFiles.objects.create(post=self.post, file=file)

        files = []
        num_created_files = 2
        for i in range(num_created_files):
            files.append(ContentFile(b'File', name=f'created file {i}.txt'))
        response = client.post(reverse('update_post', kwargs={'pk': self.post.pk}),
                               data={'text': 'test_create_attached_files',
                                     'attached_files': files})
        attached_files = AttachedFiles.objects.filter(post=self.post)
        self.assertEqual(attached_files.count(), num_created_files + num_initial_files)

    def test_delete_initial_files(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        num_initial_files = 2
        for i in range(num_initial_files):
            file = ContentFile(b'File', name=f'file {i}.txt')
            AttachedFiles.objects.create(post=self.post, file=file)

        files = []
        num_created_files = 3
        for i in range(num_created_files):
            files.append(ContentFile(b'File', name=f'created file {i}.txt'))
        response = client.post(reverse('update_post', kwargs={'pk': self.post.pk}),
                               data={'text': 'test_create_attached_files',
                                     'attached_files': files,
                                     'delete_initial': True})
        attached_files = AttachedFiles.objects.filter(post=self.post)
        self.assertEqual(attached_files.count(), num_created_files)

    def test_get_another_user_post_update_page(self):
        User.objects.create_user('Another user', password='321ewq+.')
        client = Client()
        client.login(username='Another user', password='321ewq+.')

        response = client.get(reverse('update_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 403)

    def test_post_another_user_post_update_page(self):
        User.objects.create_user('Another user', password='321ewq+.')
        client = Client()
        client.login(username='Another user', password='321ewq+.')

        response = client.post(reverse('update_post', kwargs={'pk': self.post.pk}),
                               data={'text': 'test_post_another_user_post_update_page'})
        self.assertEqual(response.status_code, 403)


class PostScoreChangeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)

        section = Sections.objects.create(name='Раздел 1')
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()
        Posts.objects.create(author=forum_user, topic=topic, text="Test message", post_type=0)

    def setUp(self):
        self.forum_user = ForumUsers.objects.get(pk=1)
        self.post = Posts.objects.get(pk=1)

    def test_allowed_only_post(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.get(reverse('rate_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 405)

    def test_redirect_not_auth_user(self):
        response = self.client.post(reverse('rate_post', kwargs={'pk': self.post.pk}),
                                    data={'value': '1'})
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_post_rate_changed(self):
        client = Client()
        client.login(username='User', password='123qwe+.')

        response = client.post(reverse('rate_post', kwargs={'pk': self.post.pk}),
                               data={'value': '1'})
        before = Statistics.objects.get(user=self.forum_user, posts=self.post).value

        response = client.post(reverse('rate_post', kwargs={'pk': self.post.pk}),
                               data={'value': '-1'})
        after = Statistics.objects.get(user=self.forum_user, posts=self.post).value

        self.assertNotEqual(before, after)


class TopicDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='User with permissions', password='123qwe+.')
        permission = Permission.objects.get(codename='delete_topics')
        user.user_permissions.add(permission)
        user.save()

        forum_user = ForumUsers.objects.get(user=user)
        section = Sections.objects.create(name='Раздел 1')
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()
        Posts.objects.create(author=forum_user, topic=topic, text="Test message", post_type=0)

    def setUp(self):
        self.topic = Topics.objects.get(pk=1)

    def test_view_uses_correct_template(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.get(reverse('delete_topic', kwargs={'pk': self.topic.pk}))
        self.assertTemplateUsed(response, 'forum/default_form_page.html')

    def test_context(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.get(reverse('delete_topic', kwargs={'pk': self.topic.pk}))
        context = response.context
        self.assertIn('title', context)
        self.assertIn('submit_value', context)
        self.assertIn('change_text', context)
        self.assertIn('form_message', context)

    def test_get_for_user_with_permission(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.get(reverse('delete_topic', kwargs={'pk': self.topic.pk}))
        self.assertEqual(response.status_code, 200)

    def test_get_for_user_without_permissions(self):
        User.objects.create(username='Default user', password='132eqw+.')
        client = Client()
        client.login(username='Default user', password='132eqw+.')
        response = client.get(reverse('delete_topic', kwargs={'pk': self.topic.pk}))
        self.assertEqual(response.status_code, 302)

    def test_success_url(self):
        section = self.topic.sections
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.post(reverse('delete_topic', kwargs={'pk': self.topic.pk}))
        self.assertRedirects(response, section.get_absolute_url())

    def test_topic_deleted(self):
        deleted_topic_url = self.topic.get_absolute_url()
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        client.post(reverse('delete_topic', kwargs={'pk': self.topic.pk}))
        response = client.get(deleted_topic_url)
        self.assertEqual(response.status_code, 404)

    def test_post_for_user_without_permissions(self):
        User.objects.create(username='Default user', password='132eqw+.')
        client = Client()
        client.login(username='Default user', password='132eqw+.')
        response = client.post(reverse('delete_topic', kwargs={'pk': self.topic.pk}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_get_for_not_auth_user(self):
        response = self.client.get(reverse('delete_topic', kwargs={'pk': self.topic.pk}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_post_for_not_auth_user(self):
        response = self.client.post(reverse('delete_topic', kwargs={'pk': self.topic.pk}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))


class PostDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='User with permissions', password='123qwe+.')
        permission = Permission.objects.get(codename='delete_posts')
        user.user_permissions.add(permission)
        user.save()

        forum_user = ForumUsers.objects.get(user=user)
        section = Sections.objects.create(name='Раздел 1')
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()
        Posts.objects.create(author=forum_user, topic=topic, text="Test message", post_type=0)

    def setUp(self):
        self.topic = Topics.objects.get(pk=1)
        self.post = Posts.objects.get(pk=1)

    def test_view_uses_correct_template(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.get(reverse('delete_post', kwargs={'pk': self.post.pk}))
        self.assertTemplateUsed(response, 'forum/default_form_page.html')

    def test_context(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.get(reverse('delete_post', kwargs={'pk': self.post.pk}))
        context = response.context
        self.assertIn('title', context)
        self.assertIn('submit_value', context)
        self.assertIn('change_text', context)
        self.assertIn('form_message', context)

    def test_get_for_user_with_permission(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.get(reverse('delete_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_get_for_user_without_permissions(self):
        User.objects.create(username='Default user', password='132eqw+.')
        client = Client()
        client.login(username='Default user', password='132eqw+.')
        response = client.get(reverse('delete_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 302)

    def test_success_url(self):
        topic = self.post.topic
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.post(reverse('delete_post', kwargs={'pk': self.post.pk}))
        self.assertRedirects(response, topic.get_absolute_url())

    def test_post_deleted(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        client.post(reverse('delete_post', kwargs={'pk': self.post.pk}))
        post, created = Posts.objects.get_or_create(pk=self.post.pk, topic=self.topic,
                                                    defaults={'text':'test_post_deleted',
                                                              'post_type':1})
        self.assertTrue(created)

    def test_post_for_user_without_permissions(self):
        User.objects.create(username='Default user', password='132eqw+.')
        client = Client()
        client.login(username='Default user', password='132eqw+.')
        response = client.post(reverse('delete_post', kwargs={'pk': self.post.pk}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_get_for_not_auth_user(self):
        response = self.client.get(reverse('delete_post', kwargs={'pk': self.post.pk}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_post_for_not_auth_user(self):
        response = self.client.post(reverse('delete_post', kwargs={'pk': self.post.pk}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))


class TopicUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='User with permissions', password='123qwe+.')
        permission = Permission.objects.get(codename='change_topics')
        user.user_permissions.add(permission)
        user.save()

        forum_user = ForumUsers.objects.get(user=user)
        section = Sections.objects.create(name='Раздел 1')
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()
        Posts.objects.create(author=forum_user, topic=topic, text="Test message", post_type=0)

    def setUp(self):
        self.topic = Topics.objects.get(pk=1)

    def test_view_uses_correct_template(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.get(reverse('change_topic', kwargs={'pk': self.topic.pk}))
        self.assertTemplateUsed(response, 'forum/default_form_page.html')

    def test_context(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.get(reverse('change_topic', kwargs={'pk': self.topic.pk}))
        context = response.context
        self.assertIn('title', context)
        self.assertIn('submit_value', context)
        self.assertIn('change_text', context)

    def test_get_for_user_with_permission(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        response = client.get(reverse('change_topic', kwargs={'pk': self.topic.pk}))
        self.assertEqual(response.status_code, 200)

    def test_get_for_user_without_permissions(self):
        User.objects.create(username='Default user', password='132eqw+.')
        client = Client()
        client.login(username='Default user', password='132eqw+.')
        response = client.get(reverse('change_topic', kwargs={'pk': self.topic.pk}))
        self.assertEqual(response.status_code, 302)

    def test_success_url(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        section = Sections.objects.create(name="New Section")
        response = client.post(reverse('change_topic', kwargs={'pk': self.topic.pk}),
                               data={'sections': section.pk, 'name': self.topic.name})
        self.assertRedirects(response, self.topic.get_absolute_url())

    def test_topic_changed(self):
        client = Client()
        client.login(username='User with permissions', password='123qwe+.')
        section = Sections.objects.create(name="New Section")
        client.post(reverse('change_topic', kwargs={'pk': self.topic.pk}),
                    data={'sections': section.pk, 'name': self.topic.name})
        topic = Topics.objects.get(pk=self.topic.pk)
        self.assertEqual(topic.sections, section)

    def test_post_for_user_without_permissions(self):
        User.objects.create(username='Default user', password='132eqw+.')
        client = Client()
        client.login(username='Default user', password='132eqw+.')
        response = client.post(reverse('change_topic', kwargs={'pk': self.topic.pk}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_get_for_not_auth_user(self):
        response = self.client.get(reverse('change_topic', kwargs={'pk': self.topic.pk}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_post_for_not_auth_user(self):
        response = self.client.post(reverse('change_topic', kwargs={'pk': self.topic.pk}))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))