from django.test import TestCase
from django.test import Client

from django.contrib.auth.models import User

from django.core.files.base import ContentFile

from django.shortcuts import reverse

from main_app.settings import LOGIN_REDIRECT_URL

class UpdateProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='User', password='123qwe+.')

    def setUp(self):
        client = Client()
        client.login(username='User', password='123qwe+.')
        self.user = User.objects.get(pk=1)
        self.client = client

    def test_view_url_exists(self):
        response = self.client.get(reverse('profile_update'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('profile_update'))
        self.assertTemplateUsed(response, 'registration/profile_form.html')

    def test_context(self):
        response = self.client.get(reverse('profile_update'))
        context = response.context
        self.assertTrue('title' in context)
        self.assertTrue('current_image' in context)
        self.assertTrue('enctype' in context)
        self.assertTrue('submit_value' in context)

    def test_redirect_not_auth_user(self):
        client = Client()
        response = client.get(reverse('profile_update'))
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_always_update_session_user_profile(self):
        # auth user
        old_user_data = self.user
        response = self.client.post(reverse('profile_update'), {'email': 'new@email.com'})
        new_user_data = User.objects.get(pk=old_user_data.pk)
        self.assertNotEqual(old_user_data.email, new_user_data.email)

        # not auth
        client = Client()
        response = client.post(reverse('profile_update'), {'email': 'new@email.com'})
        response_url = str(response.url)
        expected_url = str(reverse('login'))
        self.assertTrue(response_url.startswith(expected_url))

    def test_success_url(self):
        response = self.client.post(reverse('profile_update'), {'email': 'new@email.com'})
        self.assertRedirects(response, self.user.forumusers.get_absolute_url())


class UserDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='User', password='123qwe+.')

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_view_url_exists(self):
        response = self.client.get(reverse('profile', kwargs={'slug': self.user.forumusers.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('profile', kwargs={'slug': self.user.forumusers.slug}))
        self.assertTemplateUsed(response, 'registration/user_detail.html')

    def test_context(self):
        response = self.client.get(reverse('profile', kwargs={'slug': self.user.forumusers.slug}))
        context = response.context
        self.assertTrue('title' in context)
        self.assertTrue('can_edit' in context)


class CreateUserViewTest(TestCase):
    def test_view_url_exists(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('registration'))
        self.assertTemplateUsed(response, 'main_app/default_form_page.html')

    def test_context(self):
        response = self.client.get(reverse('registration'))
        context = response.context
        self.assertTrue('title' in context)
        self.assertTrue('submit_value' in context)

    def test_get_post_auth_user(self):
        user = User.objects.create_user(username='User', password='123qwe+.')
        client = Client()
        client.login(username='User', password='123qwe+.')
        # get
        response = client.get(reverse('registration'))
        self.assertTrue(response.status_code, 302)
        # post
        data = {'username': 'New_user', 'password1': '123qwe+.', 'password2': '123qwe+.',
                'email': 'valid@email.com',
                'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'}
        response = client.post(reverse('registration'), data=data)
        self.assertTrue(response.status_code, 302)

    def test_registration_user(self):
        data = {'username': 'New_user', 'password1': '123qwe+.', 'password2': '123qwe+.',
                'email': 'valid@email.com',
                'captcha_0': 'dummy-value', 'captcha_1': 'PASSED'}
        response = self.client.post(reverse('registration'), data=data)
        new_user = User.objects.filter(username='New_user')
        self.assertTrue(len(new_user) == 1)


class LoginViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='User', password='123qwe+.')

    def test_view_url_exists(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_not_auth_user(self):
        data = {'username': 'User', 'password': '123qwe+.'}
        response = self.client.post(reverse('login'), data=data)
        self.assertRedirects(response, LOGIN_REDIRECT_URL)


class PasswordChangeFormViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='User', password='123qwe+.')

    def setUp(self):
        client = Client()
        client.login(username='User', password='123qwe+.')
        self.client = client

    def test_view_url_exists(self):
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('password_change'))
        self.assertTemplateUsed(response, 'registration/password_change_form.html')

    def test_success_url(self):
        data = {'new_password1': 'L86kGJ62sq7cj2P', 'new_password2': 'L86kGJ62sq7cj2P',
                'old_password': '123qwe+.'}
        response = self.client.post(reverse('password_change'), data=data)
        self.assertRedirects(response, reverse('password_change_done'))

# TODO test views: 404, 403 etc.