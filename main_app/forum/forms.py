from django import forms
from .models import *
from captcha.fields import CaptchaField

class CreateTopicForm(forms.ModelForm):
    captcha = CaptchaField(label="Введите, чтобы доказать, что вы не робот.")
    text=forms.CharField(label="Текст сообщения",widget=forms.Textarea())

    def __init__(self,*args, **kwargs):
        self.section=kwargs.pop('section')
        self.user = kwargs.pop('author')
        super(CreateTopicForm, self).__init__(*args, **kwargs)

    def save(self):
        self.instance.sections=self.section
        author=ForumUsers.objects.get(user=self.user)
        self.instance.author=author
        topic=super(CreateTopicForm, self).save()
        Posts.objects.create(text=self.cleaned_data['text'],post_type=0,topic=topic,author=author)
        return topic

    class Meta:
        model = Topics
        fields = ['name','text']

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['text']