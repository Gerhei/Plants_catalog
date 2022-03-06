from django import forms
from .models import *
from captcha.fields import CaptchaField

order_choices = [('inc', 'По возрастанию'),
                 ('desc', 'По убыванию')]
order_by=[('name', 'По алфавиту'),('time_create','По дате создания',),
          ('view_count','По просмотрам')]

class FilterForm(forms.Form):
    name = forms.CharField(max_length=255,required=False,label="Название темы")
    author=forms.CharField(max_length=255,required=False,label="Автор")
    sort=forms.ChoiceField(choices=order_by,required=False,label="Сортировка по")
    order=forms.ChoiceField(choices=order_choices,required=False,label="Сортировка по")
    page = forms.IntegerField(min_value=1, label="Страница",required=False,initial=1)


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