from django.test import TestCase

from main_app.forms import *
from forum.models import ForumUsers


class MyUserFormTest(TestCase):
    def setUp(self):
        self.form = MyUserForm()

    def test_captcha_in_form(self):
        captcha_field = self.form.fields['captcha']
        self.assertEqual(type(captcha_field), CaptchaField)

    def test_clean_email(self):
        data = {'username': 'Test_user', 'password1': '123qwe+.', 'password2': '123qwe+.',
                'email': 'valid@email.com',
                'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'}
        form = MyUserForm(data)
        self.assertTrue(form.is_valid())
        form.save()

        data = {'username': 'Test_user_second', 'password1': '123qwe+.', 'password2': '123qwe+.',
                'email': 'valid@email.com',
                'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'}
        form = MyUserForm(data)
        self.assertFalse(form.is_valid())

    def test_clean_username(self):
        data = {'username': 'Very_long_username_name', 'password1': '123qwe+.', 'password2': '123qwe+.',
                'email': 'valid@email.com',
                'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'}
        form = MyUserForm(data)
        self.assertFalse(form.is_valid())


class ProfileFormTest(TestCase):
    def setUp(self):
        self.form = ProfileForm()

    def test_user_image_field_widget(self):
        user_image = self.form.fields['user_image']
        self.assertEqual(type(user_image.widget), fields.FileInput)

    def test_user_image_field_required(self):
        user_image = self.form.fields['user_image']
        self.assertFalse(user_image.required)

    def test_about_user_field_widget(self):
        about_user = self.form.fields['about_user']
        self.assertEqual(type(about_user.widget), fields.Textarea)

    def test_about_user_field_required(self):
        about_user = self.form.fields['about_user']
        self.assertFalse(about_user.required)

    def test_clean_email(self):
        data = {'email': 'valid@email.com'}
        user = User.objects.create_user(username='Test_user', password='123qwe+.')
        form = ProfileForm(instance=user, data=data)
        self.assertTrue(form.is_valid())
        form.save()

        data = {'email': 'valid@email.com'}
        user = User.objects.create_user(username='Test_user_second', password='123qwe+.')
        form = ProfileForm(instance=user, data=data)
        self.assertFalse(form.is_valid())

    def test_save_forum_user_data(self):
        data = {'email': 'valid@email.com', 'about_user': 'test text'}
        user = User.objects.create_user(username='Test_user', password='123qwe+.')
        form = ProfileForm(instance=user, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        forum_user = ForumUsers.objects.get(user=user)
        self.assertEqual(forum_user.about_user, 'test text')
