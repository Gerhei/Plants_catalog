from django import forms
from .models import *

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