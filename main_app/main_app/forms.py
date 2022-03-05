from django.contrib.auth.forms import UserCreationForm,ValidationError
from django.contrib.auth.models import User
from captcha.fields import CaptchaField

class MyUserForm(UserCreationForm):
    captcha = CaptchaField(label="Введите, чтобы доказать, что вы не робот.")

    def clean_email(self):
        data = self.cleaned_data['email']
        if data=='':
            raise ValidationError("Введите почтовый адрес.")
        all_emails=User.objects.values('email')
        for email in all_emails:
            if data==email['email']:
                raise ValidationError("Для регистрации необходим почтовый адрес, "
                                      "который еще не использовался для создания аккаунта на этом сайте.")
        return data

    class Meta(UserCreationForm.Meta):
        fields = ("username","email")