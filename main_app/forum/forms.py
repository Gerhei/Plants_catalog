from django import forms
from .models import *
from captcha.fields import CaptchaField

class CreateTopicForm(forms.ModelForm):
    captcha = CaptchaField(label="Введите, чтобы доказать, что вы не робот.")
    text=forms.CharField(label="Текст сообщения",widget=forms.Textarea())
    #section=forms.ModelChoiceField(queryset=Sections.objects.all(),widget=forms.HiddenInput())

    def __init__(self,*args, **kwargs):
        self.section=kwargs.pop('section')
        super(CreateTopicForm, self).__init__(*args, **kwargs)

    def save(self):
        # add author to topic and to post
        self.instance.sections=self.section
        topic=super(CreateTopicForm, self).save()
        Posts.objects.create(text=self.cleaned_data['text'],post_type=0,topic=topic)
        return topic

    class Meta:
        model = Topics
        fields = ['name','text']