from django.test import TestCase
from django.template.loader import render_to_string
from django.template import Context, Template
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.forms import *
from unittest import skip


class SimpleForm(Form):
    simple_field = CharField(label='test label', help_text='help text')
    hidden_field = CharField(widget=HiddenInput)

    def clean(self):
        data = self.cleaned_data['simple_field']
        if data == 'test':
            self.add_error('simple_field', 'Test field error')
            raise ValidationError('Test form error')


class BaseTemplateTest(TestCase):
    def setUp(self):
        template_name = 'main_app/base.html'
        self.rendered_template = render_to_string(template_name)

    def test_title_in_template(self):
        title = '<title></title>'
        self.assertInHTML(title, self.rendered_template)

    def test_styles_in_template(self):
        styles = '<link type="text/css" href="/static/main_app/css/styles.css" rel="stylesheet">'
        self.assertInHTML(styles, self.rendered_template)

    def test_icon_in_template(self):
        icon = '<link rel="shortcut icon" href="/static/main_app/images/site_icon.ico" type="image/x-icon">'
        self.assertInHTML(icon, self.rendered_template)


class DefaultFormPageTemplateTest(TestCase):
    def setUp(self):
        template_name = 'main_app/default_form_page.html'
        self.context = {'change_text': 'test text', 'form_message': 'test message',
                   'submit_value': 'value', 'action': 'topic/test_slug', 'form': SimpleForm()}
        self.rendered_template = render_to_string(template_name, self.context)

    def test_change_text_in_template(self):
        # In addition to the tag itself,
        # I added text inside it due to bug #24112 (although it says that it was fixed)
        change_text = '<h2 class="super-title change-text">%s</h2>' % self.context['change_text']
        self.assertInHTML(change_text, self.rendered_template)

    def test_form_message_in_template(self):
        form_message = '<p class="form-message">%s</p>' % self.context['form_message']
        self.assertInHTML(form_message, self.rendered_template)

    def test_submit_in_template(self):
        submit = '<div class="field-input"><input type="submit" value="%s"></div>' % self.context['submit_value']
        self.assertInHTML(submit, self.rendered_template)


class DefaultPostFormTemplateTest(TestCase):
    def setUp(self):
        template_name = 'main_app/default_post_form.html'
        self.form = SimpleForm(data={'simple_field': 'test', 'hidden_field': 'test'})
        self.form.is_valid()
        self.context = {'form': self.form}
        self.rendered_template = render_to_string(template_name, self.context)

    def test_form_errors_in_template(self):
        form_errors = '<ul class="errornote"></ul>'
        self.assertInHTML(form_errors, self.rendered_template)

    @skip
    def test_hidden_fields_in_template(self):
        # bug 24112
        hidden_fields = '<div class="hidden-field">%s</div>' % self.form.cleaned_data['hidden_field']
        self.assertInHTML(hidden_fields, self.rendered_template)

    @skip
    def test_visible_field_in_template(self):
        # bug 24112
        pass


class FooterTemplateTest(TestCase):
    def setUp(self):
        template_name = 'main_app/footer.html'
        self.rendered_template = render_to_string(template_name)


class IndexTemplateTest(TestCase):
    def setUp(self):
        template_name = 'main_app/index.html'
        self.rendered_template = render_to_string(template_name)


class HeaderTemplateTest(TestCase):
    def setUp(self):
        template_name = 'main_app/header.html'
        self.rendered_template = render_to_string(template_name)


class NavigationTemplateTest(TestCase):
    def setUp(self):
        template_name = 'main_app/navigation.html'
        self.rendered_template = render_to_string(template_name)


class PaginationTemplateTest(TestCase):
    def setUp(self):
        template_name = 'main_app/pagination.html'
        objects = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        paginator = Paginator(objects, 1)
        page_obj = paginator.get_page(5)
        context = {'page_obj': page_obj}
        self.rendered_template = render_to_string(template_name, context)

    @skip
    def test_previous_in_template(self):
        # bug 24112
        pass

    @skip
    def test_current_in_template(self):
        # bug 24112
        current = '<span class="current">'
        self.assertInHTML(current, self.rendered_template)

    @skip
    def test_last_in_template(self):
        # bug 24112
        pass


class LoggedOutTemplateTest(TestCase):
    def setUp(self):
        template_name = 'registration/logged_out.html'
        self.rendered_template = render_to_string(template_name)


class LoginTemplateTest(TestCase):
    def setUp(self):
        template_name = 'registration/login.html'
        self.rendered_template = render_to_string(template_name)


class PasswordChangeFormTemplateTest(TestCase):
    def setUp(self):
        template_name = 'registration/password_change_form.html'
        self.rendered_template = render_to_string(template_name, {'form': SimpleForm()})

    def test_form_message_in_template(self):
        form_message = '{% load i18n static %}' \
                       '<p class="text-padding">{% translate ' \
                       '\'Please enter your old password, for security’s sake, ' \
                       'and then enter your new password twice ' \
                       'so we can verify you typed it in correctly.\' %}</p>'
        form_message = Template(form_message).render(Context())
        self.assertInHTML(form_message, self.rendered_template)


class PasswordResetCompleteTemplateTest(TestCase):
    def setUp(self):
        template_name = 'registration/password_reset_complete.html'
        self.rendered_template = render_to_string(template_name)

    def test_login_url_in_template(self):
        login_url = '{% load i18n static %}' \
                    '<p><a href="{{ login_url }}" class="app_link">{% translate \'Log in\' %}</a></p>'
        login_url = Template(login_url).render(Context())
        self.assertInHTML(login_url, self.rendered_template)


class PasswordResetConfirmTemplateTest(TestCase):
    def setUp(self):
        template_name = 'registration/password_reset_confirm.html'
        self.rendered_template = render_to_string(template_name, {'validlink': True, 'form': SimpleForm()})

    def test_form_message_in_template(self):
        form_message = '{% load i18n static %}' \
                       '<div class="text-padding">{% translate ' \
                       '"Please enter your new password twice so we can verify you typed it in correctly." %}' \
                       '</div>'
        form_message = Template(form_message).render(Context())
        self.assertInHTML(form_message, self.rendered_template)


class PasswordResetFormTemplateTest(TestCase):
    def setUp(self):
        template_name = 'registration/password_reset_form.html'
        self.rendered_template = render_to_string(template_name, {'form': SimpleForm()})

    def test_form_message_in_tempalte(self):
        form_message = '{% load i18n static %}' \
                       '<div class="text-padding">' \
                       '{% translate \'Forgotten your password? Enter your email address below, ' \
                                    'and we’ll email instructions for setting a new one.\' %}' \
                        '</div>'
        form_message = Template(form_message).render(Context())
        self.assertInHTML(form_message, self.rendered_template)


class UserDetailTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='User', password='123qwe+.')

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.template_name = 'registration/user_detail.html'
        self.rendered_template = render_to_string(self.template_name, {'object': self.user, 'can_edit': True})

    def test_extrastyles_in_template(self):
        extrastyles = '<link type="text/css" href="/static/main_app/css/profile_detail.css" rel="stylesheet"/>'
        self.assertInHTML(extrastyles, self.rendered_template)

    @skip
    def test_can_edit_profile(self):
        # bug 24112
        edit_profile = '<div class="profile-editing">' \
                       '<p class="profile-edit"><a href="{% url \'profile_update\' %}" class="app_link">'
        edit_profile = Template(edit_profile).render(Context())
        # can edit
        self.assertInHTML(edit_profile, self.rendered_template)

        # can't edit
        self.rendered_template = render_to_string(self.template_name, {'object': self.user, 'can_edit': False})
        self.assertInHTML(edit_profile, self.rendered_template, count=0)
