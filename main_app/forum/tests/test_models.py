from django.test import TestCase

from forum.models import *

from django.core.validators import MinValueValidator
from django.core.files.base import ContentFile

from slugify import slugify
from main_app.settings import MAX_USERNAME_LENGTH

from django.contrib.auth.models import User

import time


class SectionsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super_sections = Sections(name='Главный раздел',super_sections=None)
        super_sections.save()
        sub_sections = Sections(name='Раздел 1',super_sections=super_sections)
        sub_sections.save()

    def setUp(self):
        self.super_sections = Sections.objects.get(name='Главный раздел')
        self.sub_sections = Sections.objects.get(name='Раздел 1')

    def test_str_method(self):
        self.assertEquals(self.super_sections.name, self.super_sections.__str__())
        self.assertEquals(self.sub_sections.name, self.sub_sections.__str__())

    def test_get_absolute_url(self):
        url = reverse('topics', kwargs={'slug': self.super_sections.slug})
        self.assertEquals(self.super_sections.get_absolute_url(), url)

    def test_name_unique(self):
        unique = self.super_sections._meta.get_field('name').unique
        self.assertEquals(unique, True)

    def test_name_max_length(self):
        max_length = self.super_sections._meta.get_field('name').max_length
        self.assertEquals(max_length, 40)

    def test_name_lower_editable(self):
        editable = self.super_sections._meta.get_field('name_lower').editable
        self.assertEquals(editable, False)

    def test_correct_creation_name_lower(self):
        name_lower = self.super_sections.name_lower
        self.assertEquals(name_lower, self.super_sections.name.lower())

    def test_order_default(self):
        default = self.super_sections._meta.get_field('order').default
        self.assertEquals(default, 0)

    def test_order_editable(self):
        editable = self.super_sections._meta.get_field('order').editable
        self.assertEquals(editable, False)

    def test_correct_creation_order(self):
        super_order=self.super_sections.order
        sub_order=self.sub_sections.order
        self.assertEquals(super_order, 0)
        self.assertEquals(sub_order,self.sub_sections.super_sections.order + 1)

    def test_slug_editable(self):
        editable = self.super_sections._meta.get_field('slug').editable
        self.assertEquals(editable, False)

    def test_slug_unique(self):
        unique = self.super_sections._meta.get_field('slug').unique
        self.assertEquals(unique, True)

    def test_correct_creation_slug(self):
        super_slug = self.super_sections.slug
        sub_slug = self.sub_sections.slug
        self.assertEquals(super_slug, slugify(self.super_sections.name))
        self.assertEquals(sub_slug, slugify(self.sub_sections.name))

    def test_super_sections_null(self):
        is_null = self.super_sections._meta.get_field('super_sections').null
        self.assertEquals(is_null, True)


class TopicsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)
        section = Sections(name='Раздел 1')
        section.save()
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()

    def setUp(self):
        self.topic = Topics.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(f'{self.topic.name}-{self.topic.pk}', self.topic.__str__())

    def test_get_absolute_url(self):
        url = reverse('topic', kwargs={'slug': self.topic.slug})
        self.assertEquals(self.topic.get_absolute_url(), url)

    def test_name_max_length(self):
        max_length = self.topic._meta.get_field('name').max_length
        self.assertEquals(max_length, 40)

    def test_name_lower_editable(self):
        editable = self.topic._meta.get_field('name_lower').editable
        self.assertEquals(editable, False)

    def test_correct_creation_name_lower(self):
        name_lower = self.topic.name_lower
        self.assertEquals(name_lower,self.topic.name.lower())

    def test_slug_editable(self):
        editable = self.topic._meta.get_field('slug').editable
        self.assertEquals(editable, False)

    def test_slug_unique(self):
        unique = self.topic._meta.get_field('slug').unique
        self.assertEquals(unique, True)

    def test_correct_creation_slug(self):
        slug=self.topic.slug
        self.assertEquals(slug,slugify(f'{self.topic.name}_{self.topic.pk}'))

    def test_view_count_editable(self):
        editable = self.topic._meta.get_field('view_count').editable
        self.assertEquals(editable, False)

    def test_view_count_validators(self):
        validators = self.topic._meta.get_field('view_count').validators
        self.assertEquals(validators, [MinValueValidator(0)])

    def test_view_count_default(self):
        default = self.topic._meta.get_field('view_count').default
        self.assertEquals(default, 0)

    def test_author_null(self):
        null = self.topic._meta.get_field('author').null
        self.assertEquals(null, True)

    def test_ordering(self):
        ordering = self.topic._meta.ordering
        self.assertEquals(ordering, ('time_create', 'name'))

    def test_f_value_when_saving(self):
        before = self.topic.view_count
        self.topic.view_count = F('view_count') + 1
        self.topic.save()
        after = self.topic.view_count
        self.assertEquals(before + 1, after)


class PostsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)
        section = Sections(name='Раздел 1')
        section.save()
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()
        Posts.objects.create(author=forum_user, topic=topic, text="Test message", post_type=0)

    def setUp(self):
        self.post = Posts.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(f'Сообщение-{self.post.pk}', self.post.__str__())

    def test_author_null(self):
        null = self.post._meta.get_field('author').null
        self.assertEquals(null, True)

    def test_post_type_choices(self):
        choices = self.post._meta.get_field('post_type').choices
        self.assertEquals(choices, ((0,'question'),(1,'answer')))

    def test_is_changed(self):
        self.post.text = "test message"
        time.sleep(1)
        self.post.save()
        self.assertEquals(self.post.is_changed(), True)

    def test_is_user_can_edit(self):
        user = User.objects.create_user('UserUser', password='123qwe++ewq321.')
        forum_user = ForumUsers.objects.get(user=user)
        self.assertEquals(self.post.is_user_can_edit(forum_user), False)

    def test_ordering(self):
        ordering = self.post._meta.ordering
        self.assertEquals(ordering, ('topic', 'post_type', 'time_create', 'author'))


class ForumUsersModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        ForumUsers.objects.get(user=user)

    def setUp(self):
        self.forum_user = ForumUsers.objects.get(pk=1)

    def test_auto_create_forum_user_when_create_user(self):
        user = User.objects.create_user('UserUSer', password='123qwe++ewq321.')
        forum_user = ForumUsers.objects.get(user=user)
        self.assertEquals(user.forumusers, forum_user)

    def test_str_method(self):
        self.assertEquals(self.forum_user.username_lower, self.forum_user.__str__())

    def test_username_lower_max_length(self):
        max_length = self.forum_user._meta.get_field('username_lower').max_length
        self.assertEquals(max_length, MAX_USERNAME_LENGTH)

    def test_username_lower_editable(self):
        editable = self.forum_user._meta.get_field('username_lower').editable
        self.assertEquals(editable, False)

    def test_correct_creation_username_lower(self):
        username_lower=self.forum_user.username_lower
        self.assertEquals(username_lower,self.forum_user.user.username.lower())

    def test_user_image_blank(self):
        blank = self.forum_user._meta.get_field('user_image').blank
        self.assertEquals(blank, True)

    def test_about_user_blank(self):
        blank = self.forum_user._meta.get_field('about_user').blank
        self.assertEquals(blank, True)

    def test_reputation_default(self):
        default = self.forum_user._meta.get_field('reputation').default
        self.assertEquals(default, 0)

    def test_slug_editable(self):
        editable = self.forum_user._meta.get_field('slug').editable
        self.assertEquals(editable, False)

    def test_slug_unique(self):
        unique = self.forum_user._meta.get_field('slug').unique
        self.assertEquals(unique, True)

    def test_correct_creation_slug(self):
        slug = self.forum_user.slug
        self.assertEquals(slug, slugify(self.forum_user.user.username))

    def test_user_image_default(self):
        default = self.forum_user._meta.get_field('user_image').default
        self.assertEquals(default, '/forum/user_images/default_profile.jpg')


class AttachedFilesModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)
        section = Sections(name='Раздел 1')
        section.save()
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()
        post = Posts.objects.create(author=forum_user, topic=topic, text="Test message", post_type=0)

        content_file = ContentFile(b'Hello world!', name='hello-world.txt')
        AttachedFiles.objects.create(post=post, file=content_file)

    def setUp(self):
        self.attached_file = AttachedFiles.objects.get(pk=1)

    def test_max_files_per_post(self):
        max_files_per_post = self.attached_file.max_files_per_post
        self.assertEquals(max_files_per_post, 10)

    def test_file_validators(self):
        validators = self.attached_file._meta.get_field('file').validators
        self.assertEquals(validators, [FileExtensionValidator(allowed_extensions=
                                                              self.attached_file.allowed_ext)])

    def test_str_method(self):
        self.assertEquals(self.attached_file.file.name, self.attached_file.__str__())

    def test_get_absolute_url(self):
        url = self.attached_file.file.url
        self.assertEquals(url, self.attached_file.get_absolute_url())

    def test_ordering(self):
        ordering = self.attached_file._meta.ordering
        self.assertEquals(ordering, ('time_create',))

    def test_clean(self):
        post = self.attached_file.post
        for i in range(self.attached_file.max_files_per_post):
            AttachedFiles.objects.create(post=post)

        self.assertRaises(ValidationError, self.attached_file.full_clean)


class StatisticsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)
        value = 1

        section = Sections.objects.create(name='Раздел 1')
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()
        post = Posts.objects.create(author=forum_user, topic=topic, text="Test message", post_type=0)

        Statistics.objects.create(user=forum_user, value=value, content_object=post, value_type=0)
        Statistics.objects.create(user=forum_user, value=value, content_object=topic, value_type=1)

    def setUp(self):
        self.forum_user = ForumUsers.objects.get(pk=1)
        self.section = Sections.objects.get(pk=1)
        self.topic = Topics.objects.get(pk=1)
        self.post = Posts.objects.get(pk=1)
        self.post_statistics = Statistics.objects.get(value_type=0)
        self.topic_statistics = Statistics.objects.get(value_type=1)

    def test_str_method(self):
        str = f'{self.post_statistics.user} {self.post_statistics.content_type}-' \
              f'{self.post_statistics.object_id}'
        self.assertEquals(self.post_statistics.__str__(), str)

        str = f'{self.topic_statistics.user} {self.topic_statistics.content_type}-' \
              f'{self.topic_statistics.object_id}'
        self.assertEquals(self.topic_statistics.__str__(), str)

    def test_unique_together(self):
        unique_together = self.post_statistics._meta.unique_together
        self.assertEquals(unique_together, (('user', 'value_type', 'object_id'),))

    def test_does_not_support_statistics(self):
        statistic = Statistics(user=self.forum_user, value_type=0, content_object=self.section)
        self.assertRaises(ValidationError, statistic.save)

    # TODO  Add tests:
    #       view_count_change; user_reputation_Change