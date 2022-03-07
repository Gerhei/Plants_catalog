from django.forms import forms, fields,models
from django.contrib.auth.forms import UserCreationForm,ValidationError
from django.contrib.auth.models import User
from captcha.fields import CaptchaField

def clean_email(data):
    if data == '':
        raise ValidationError("Введите почтовый адрес.")
    all_emails = User.objects.values('email')
    for email in all_emails:
        if data == email['email']:
            raise ValidationError("Для регистрации необходим почтовый адрес, "
                                  "который еще не использовался для создания аккаунта на этом сайте.")
    return data

class MyUserForm(UserCreationForm):
    captcha = CaptchaField(label="Введите, чтобы доказать, что вы не робот.")

    def clean_email(self):
        data = self.cleaned_data['email']
        data=clean_email(data)
        return data

    class Meta(UserCreationForm.Meta):
        fields = ("username","email")


class EmailForm(forms.Form):
    #captcha = CaptchaField(label="Введите, чтобы доказать, что вы не робот.")
    email=fields.EmailField(label="Адрес почты")

    def clean_email(self):
        data = self.cleaned_data['email']
        data = clean_email(data)
        return data
