from django.test import TestCase
from forum.forms import *


class FilterFormTest(TestCase):
    def setUp(self):
        self.form = FilterForm()

    def test_name_required(self):
        required = self.form.fields['name'].required
        self.assertEquals(required, False)

    def test_sort_required(self):
        required = self.form.fields['sort'].required
        self.assertEquals(required, False)

    def test_sort_choices(self):
        choices = self.form.fields['sort'].choices
        self.assertEquals(choices, order_by)

    def test_order_required(self):
        required = self.form.fields['order'].required
        self.assertEquals(required, False)

    def test_order_choices(self):
        choices = self.form.fields['order'].choices
        self.assertEquals(choices, order_choices)

    def test_page_required(self):
        required = self.form.fields['page'].required
        self.assertEquals(required, False)

    def test_page_min_value(self):
        min_value = self.form.fields['page'].min_value
        self.assertEquals(min_value, 1)


class CreateTopicFormTest(TestCase):
    def setUp(self):
        self.form = CreateTopicForm()

    def test_captcha_in_form(self):
        captcha_field = self.form.fields['captcha']
        self.assertEqual(type(captcha_field), CaptchaField)

    def test_text_field_widget(self):
        text_field = self.form.fields['text']
        self.assertEqual(type(text_field.widget), forms.Textarea)

    def test_attached_files_field_widget(self):
        attached_files_field = self.form.fields['attached_files']
        self.assertEqual(type(attached_files_field.widget),
                         forms.ClearableFileInput)

    def test_attached_files_field_widget_multiple(self):
        attached_files_widget = self.form.fields['attached_files'].widget
        self.assertTrue(attached_files_widget.attrs['multiple'])

    def test_attached_files_field_required(self):
        attached_files_field = self.form.fields['attached_files']
        self.assertFalse(attached_files_field.required)

    def test_attached_files_field_help_text(self):
        attached_files_field = self.form.fields['attached_files']
        self.assertNotEqual(attached_files_field.help_text, "")

    def test_attached_files_field_allow_empty(self):
        attached_files_field = self.form.fields['attached_files']
        self.assertTrue(attached_files_field.allow_empty_file)

    def test_create_post_when_create_topic(self):
        section = Sections.objects.create(name="Test section")
        user = User.objects.create_user(username='Username', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)

        data = {'name': 'Test topic', 'text': 'Test post message',
                'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'}

        form = CreateTopicForm(data=data, section=section, author=forum_user)
        topic = form.save()
        post, created = Posts.objects.get_or_create(topic=topic, post_type=0,
                                                    author=forum_user,
                                                    text='Test post message')
        self.assertFalse(created)


class CreatePostFormTest(TestCase):
    def setUp(self):
        self.form = CreatePostForm()

    def test_attached_files_field_widget(self):
        attached_files_field = self.form.fields['attached_files']
        self.assertEqual(type(attached_files_field.widget),
                         forms.ClearableFileInput)

    def test_attached_files_field_widget_multiple(self):
        attached_files_widget = self.form.fields['attached_files'].widget
        self.assertTrue(attached_files_widget.attrs['multiple'])

    def test_attached_files_field_required(self):
        attached_files_field = self.form.fields['attached_files']
        self.assertFalse(attached_files_field.required)

    def test_attached_files_field_help_text(self):
        attached_files_field = self.form.fields['attached_files']
        self.assertNotEqual(attached_files_field.help_text, "")

    def test_attached_files_field_allow_empty(self):
        attached_files_field = self.form.fields['attached_files']
        self.assertTrue(attached_files_field.allow_empty_file)


class UpdateScorePostFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user('User', password='123qwe+.')
        forum_user = ForumUsers.objects.get(user=user)

        section = Sections.objects.create(name='Test section')
        topic = Topics(name='Test topic', author=forum_user, sections=section)
        topic.save()
        Posts.objects.create(author=forum_user, topic=topic, text="Test message", post_type=0)

    def setUp(self):
        self.form = UpdateScorePostForm()
        self.forum_user = ForumUsers.objects.get(pk=1)
        self.model_post = Posts.objects.get(pk=1)

    def test_value_field_min_max(self):
        value_field = self.form.fields['value']
        self.assertEqual(value_field.min_value, -1)
        self.assertEqual(value_field.max_value, 1)

    def test_save_old_equal_new(self):
        old_statistic = Statistics.objects.create(content_object=self.model_post, value=-1,
                                              user=self.forum_user)

        data = {'value': -1}
        form = UpdateScorePostForm(data=data, post=self.model_post, forum_user=self.forum_user)
        self.assertTrue(form.is_valid())
        new_statistic = form.save()
        self.assertEqual(old_statistic, new_statistic)

    def test_save_new_equal_zero(self):
        old_statistic = Statistics.objects.create(content_object=self.model_post, value=-1,
                                                  user=self.forum_user)

        data = {'value': 0}
        form = UpdateScorePostForm(data=data, post=self.model_post, forum_user=self.forum_user)
        self.assertTrue(form.is_valid())
        new_statistic = form.save()
        self.assertEqual(new_statistic, None)

    def test_save_new_not_equal_old_or_zero(self):
        old_statistic = Statistics.objects.create(content_object=self.model_post, value=-1,
                                                  user=self.forum_user)

        data = {'value': 1}
        form = UpdateScorePostForm(data=data, post=self.model_post, forum_user=self.forum_user)
        self.assertTrue(form.is_valid())
        new_statistic = form.save()
        self.assertNotEqual(old_statistic, new_statistic)
        self.assertNotEqual(old_statistic.value, new_statistic.value)

    def test_old_does_not_exists(self):
        data = {'value': 0}
        form = UpdateScorePostForm(data=data, post=self.model_post, forum_user=self.forum_user)
        self.assertTrue(form.is_valid())
        new_statistic = form.save()
        self.assertEqual(new_statistic, None)

        data = {'value': 1}
        form = UpdateScorePostForm(data=data, post=self.model_post, forum_user=self.forum_user)
        self.assertTrue(form.is_valid())
        new_statistic = form.save()
        self.assertEqual(new_statistic.value, 1)