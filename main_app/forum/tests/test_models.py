from django.test import TestCase
from forum.models import *
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from slugify import slugify

class SectionsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super_sections=Sections(name='Главный раздел',super_sections=None)
        super_sections.save()
        sub_sections=Sections(name='Раздел 1',super_sections=super_sections)
        sub_sections.save()

    def setUp(self):
        self.super_sections=Sections.objects.get(name='Главный раздел')
        self.sub_sections=Sections.objects.get(name='Раздел 1')

    def test_str_method(self):
        self.assertEquals(self.super_sections.name, self.super_sections.__str__())
        self.assertEquals(self.sub_sections.name, self.sub_sections.__str__())

    def test_name_unique(self):
        unique = self.super_sections._meta.get_field('name').unique
        self.assertEquals(unique, True)

    def test_name_lower_editable(self):
        editable = self.super_sections._meta.get_field('name_lower').editable
        self.assertEquals(editable, False)

    def test_correct_creation_name_lower(self):
        name_lower=self.super_sections.name_lower
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
        self.assertEquals(sub_order,self.sub_sections.super_sections.order+1)

    def test_slug_editable(self):
        editable = self.super_sections._meta.get_field('slug').editable
        self.assertEquals(editable, False)

    def test_slug_unique(self):
        unique = self.super_sections._meta.get_field('slug').unique
        self.assertEquals(unique, True)

    def test_correct_creation_slug(self):
        super_slug=self.super_sections.slug
        sub_slug=self.sub_sections.slug
        self.assertEquals(super_slug, slugify(self.super_sections.name))
        self.assertEquals(sub_slug, slugify(f'{self.sub_sections.super_sections.name}-{self.sub_sections.name}'))

    def test_super_sections_null(self):
        is_null = self.super_sections._meta.get_field('super_sections').null
        self.assertEquals(is_null, True)

    def test_unique_together(self):
        unique_together = self.super_sections._meta.unique_together
        self.assertEquals(unique_together, (('name', 'order'),))



class TopicsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user=User.objects.create_user('User',password='123qwe+.')
        section=Sections(name='Раздел 1')
        section.save()
        forum_user=ForumUsers.objects.create(user=user)
        topic=Topics(name='Тема про цветы',author=forum_user,sections=section)
        topic.save()

    def setUp(self):
        self.topic=Topics.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(self.topic.name, self.topic.__str__())

    def test_get_absolute_url(self):
        self.assertEquals(self.topic.get_absolute_url(), f'/forum/topics/{self.topic.slug}')

    def test_name_lower_editable(self):
        editable = self.topic._meta.get_field('name_lower').editable
        self.assertEquals(editable, False)

    def test_correct_creation_name_lower(self):
        name_lower=self.topic.name_lower
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
        validators=self.topic._meta.get_field('view_count').validators
        self.assertEquals(validators,[MinValueValidator(0)])

    def test_view_count_default(self):
        default = self.topic._meta.get_field('view_count').default
        self.assertEquals(default, 0)

    def test_author_null(self):
        null = self.topic._meta.get_field('author').null
        self.assertEquals(null, True)


class PostsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        section = Sections(name='Раздел 1')
        section.save()
        forum_user = ForumUsers.objects.create(user=user)
        topic = Topics(name='Тема про цветы', author=forum_user, sections=section)
        topic.save()

        Posts.objects.create(author=forum_user,topic=topic,text="Test message",post_type=0)

    def setUp(self):
        self.post = Posts.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(f'{self.post.author}:{self.post.topic}', self.post.__str__())

    def test_author_null(self):
        null = self.post._meta.get_field('author').null
        self.assertEquals(null, True)

    def test_post_type_choices(self):
        choices = self.post._meta.get_field('post_type').choices
        self.assertEquals(choices, ((0,'question'),(1,'answer')))

    def test_score_default(self):
        default = self.post._meta.get_field('score').default
        self.assertEquals(default, 0)


class ForumUsersModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        ForumUsers.objects.create(user=user)

    def setUp(self):
        self.forum_user = ForumUsers.objects.get(pk=1)

    def test_str_method(self):
        self.assertEquals(self.forum_user.user.username, self.forum_user.__str__())

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
        slug=self.forum_user.slug
        self.assertEquals(slug,slugify(self.forum_user.user.username))