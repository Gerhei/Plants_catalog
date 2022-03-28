from django import forms
from .models import *
from django.db.models import F, Value, ObjectDoesNotExist
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
    captcha = CaptchaField(label="Введите, чтобы доказать, что вы не робот")
    text=forms.CharField(label="Текст сообщения",widget=forms.Textarea())

    def __init__(self,section=None,author=None,*args, **kwargs):
        self.section=section
        self.user = author
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
        fields = ['name','captcha','text']

class CreatePostForm(forms.ModelForm):
    def __init__(self,topic=None,author=None,post_type=1,*args,**kwargs):
        self.topic=topic
        self.author=author
        self.post_type=post_type
        super(CreatePostForm, self).__init__(*args,**kwargs)
        
    def save(self):
        self.instance.topic=self.topic
        self.instance.author=self.author
        self.instance.post_type=self.post_type
        return super(CreatePostForm, self).save()

    class Meta:
        model = Posts
        fields = ['text']


class UpdateScorePostForm(forms.ModelForm):
    value=forms.IntegerField(min_value=-1,max_value=1,
                             widget=forms.RadioSelect(choices=((-1,'-'),(0,'0'),(1,'+'))),
                             label="Ваша оценка")

    def __init__(self,post=None,forum_user=None,*args, **kwargs):
        self.forum_user=forum_user
        self.post=post
        super(UpdateScorePostForm, self).__init__(*args, **kwargs)

    def save(self):
        try:
            self.instance = Statistics.objects.get(user=self.forum_user, posts=self.post)
            new_value=self.cleaned_data['value']
            old_value=self.instance.value
            if old_value == new_value:
                return
            elif new_value==0:
                self.instance.delete()
                return
            else:
                self.instance.delete()
                raise ObjectDoesNotExist

        except ObjectDoesNotExist:
            if self.cleaned_data['value']==0:
                return
            self.instance = Statistics(user=self.forum_user, value=self.cleaned_data['value'], content_object=self.post)

        return super(UpdateScorePostForm, self).save()

    class Meta:
        model = Statistics
        fields = ['value']