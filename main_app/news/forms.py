from django import forms
from .models import *

from captcha.fields import CaptchaField


order_choices = [('inc', 'По возрастанию'),
                 ('desc', 'По убыванию')]

order_by = [('publication_date', 'По дате публикации'), ('title', 'По алфавиту')]

YEARS = [year for year in range(2000, 2030)]

class FilterForm(forms.Form):
    title = forms.CharField(max_length=255, required=False, label="Название")
    publication_date = forms.DateField(required=False,
                                       widget=forms.SelectDateWidget(years=YEARS),
                                       label="Дата публикации")
    sort = forms.ChoiceField(choices=order_by, required=False, label="Сортировка по")
    order = forms.ChoiceField(choices=order_choices, required=False, label="Сортировка по")
    page = forms.IntegerField(min_value=1, required=False, initial=1, label="Страница")


class CreateCommentForm(forms.ModelForm):
    text = forms.CharField(max_length=1000,
                           widget = forms.Textarea,
                           label='Комментарий')

    def __init__(self, news=None, user=None, *args, **kwargs):
        super(CreateCommentForm, self).__init__(*args, **kwargs)
        self.news = news
        if isinstance(user, User):
            self.user = user
        else:
            self.user = None
            self.fields['captcha'] = CaptchaField(label="Введите, чтобы доказать, что вы не робот")

    def save(self):
        comment = super(CreateCommentForm, self).save(commit=False)
        comment.news = self.news
        comment.user = self.user
        comment.save()
        return comment

    class Meta:
        model = Comments
        fields = ('text',)