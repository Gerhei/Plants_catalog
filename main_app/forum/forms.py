from django import forms

from django.db.models import ObjectDoesNotExist
from .models import *

from captcha.fields import CaptchaField


order_choices = [('inc', 'По возрастанию'),
                 ('desc', 'По убыванию')]
order_by = [('name', 'По алфавиту'), ('time_create', 'По дате создания'),
            ('view_count', 'По просмотрам')]


class FilterForm(forms.Form):
    name = forms.CharField(max_length=255, required=False, label="Название темы")
    author = forms.CharField(max_length=255, required=False, label="Автор")
    sort = forms.ChoiceField(choices=order_by, required=False, label="Сортировка по")
    order = forms.ChoiceField(choices=order_choices, required=False, label="Сортировка по")
    page = forms.IntegerField(min_value=1, required=False, initial=1, label="Страница")


class CreateTopicForm(forms.ModelForm):
    captcha = CaptchaField(label="Введите, чтобы доказать, что вы не робот")
    text = forms.CharField(label="Текст сообщения", widget=forms.Textarea())
    attached_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),
                                     required=False, allow_empty_file=True,
                                     label='Прикрепленные файлы',
                                     help_text=('Не более 10 файлов, допустимые форматы '
                                                'файлов: изображения, текстовые, '
                                                'таблицы, презентации.'))

    def __init__(self, section=None, author=None, *args, **kwargs):
        super(CreateTopicForm, self).__init__(*args, **kwargs)
        self.section = section
        self.forumuser = author

    def save(self):
        topic = super(CreateTopicForm, self).save(commit=False)
        topic.sections = self.section
        topic.author = self.forumuser
        topic.save()
        # when creating a topic, create the first post
        Posts.objects.create(text=self.cleaned_data['text'], post_type=0,
                             topic=topic, author=self.forumuser)
        return topic

    class Meta:
        model = Topics
        fields = ('name', 'text', 'attached_files', 'captcha')


class CreatePostForm(forms.ModelForm):
    attached_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),
                                     required=False, allow_empty_file=True, label='Прикрепленные файлы',
                                     help_text=('Не более 10 файлов, допустимые форматы файлов: '
                                                'изображения, текстовые, таблицы, презентации.'))

    def __init__(self, topic=None, author=None, post_type=1, *args, **kwargs):
        self.topic = topic
        self.author = author
        self.post_type = post_type
        super(CreatePostForm, self).__init__(*args, **kwargs)
        
    def save(self):
        post = super(CreatePostForm, self).save(commit=False)
        post.topic = self.topic
        post.author = self.author
        post.post_type = self.post_type
        post.save()
        return post

    class Meta:
        model = Posts
        fields = ('text', 'attached_files')


class UpdateScorePostForm(forms.ModelForm):
    value = forms.IntegerField(min_value=-1, max_value=1,
                               widget=forms.RadioSelect(choices=((-1,'-'), (0,'0'), (1,'+'))),
                               label="Ваша оценка")

    def __init__(self, post=None, forum_user=None, *args, **kwargs):
        self.forum_user = forum_user
        self.post = post
        super(UpdateScorePostForm, self).__init__(*args, **kwargs)

    def save(self):
        try:
            self.instance = Statistics.objects.get(user=self.forum_user, posts=self.post)
            new_value = self.cleaned_data['value']
            old_value = self.instance.value

            # if the values match, no sense to save the model instance
            if old_value == new_value:
                return self.instance
            # if the new value = 0 , there is no sense in storing the model instance
            elif new_value == 0:
                self.instance.delete()
                return None
            # if new value not equal old_value or zero
            else:
                # instead of changing the value of a statistics it easier to create a new one
                self.instance.delete()
                raise ObjectDoesNotExist

        except ObjectDoesNotExist:
            if self.cleaned_data['value'] == 0:
                return None
            self.instance = Statistics(user=self.forum_user, value=self.cleaned_data['value'],
                                       content_object=self.post)

        return super(UpdateScorePostForm, self).save()

    class Meta:
        model = Statistics
        fields = ('value',)