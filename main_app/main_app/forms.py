from django.forms import models, fields
from django.contrib.auth.forms import UserCreationForm, ValidationError
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField


def clean_email(data):
    if data == '':
        raise ValidationError(_("Enter your email address."))
    all_emails = User.objects.values('email')
    for email in all_emails:
        if data == email['email']:
            raise ValidationError(
                _("To register, you need email address that has not yet been used to create an account on this site."))
    return data


class MyUserForm(UserCreationForm):
    captcha = CaptchaField(label=_("Enter to prove that you are not a robot."))

    def clean_email(self):
        data = self.cleaned_data['email']
        data = clean_email(data)
        return data

    def clean_username(self):
        data = self.cleaned_data['username']
        if len(data) > 20:
            raise ValidationError(_("The length of the user name can't exceed 20 characters."))
        return data

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")


class ProfileForm(models.ModelForm):
    user_image = fields.ImageField(required=False, label=_("User image"),
                                   widget=fields.FileInput())
    about_user = fields.CharField(required=False, label=_("About user"), widget=fields.Textarea)

    def save(self):
        forum_user = self.instance.forumusers
        forum_user.user_image = self.cleaned_data['user_image']
        forum_user.about_user = self.cleaned_data['about_user']
        forum_user.save()
        return super(ProfileForm, self).save()

    def clean_email(self):
        data = self.cleaned_data['email']
        # if the email is not changed
        if self.instance.email == data:
            return data
        data = clean_email(data)
        return data

    class Meta():
        model = User
        fields = ("user_image", "email", "about_user")
