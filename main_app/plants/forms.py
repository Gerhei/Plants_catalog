from django import forms
from .models import *

order_choices = [('inc', 'По возрастанию'),
                 ('desc', 'По убыванию')]

order_by=[('name', 'По алфавиту')]

class FilterForm(forms.Form):
    name = forms.CharField(max_length=255,required=False,label="Название")
    sort=forms.ChoiceField(choices=order_by,required=False,label="Сортировка по")
    order=forms.ChoiceField(choices=order_choices,required=False,label="Сортировка по")
    page = forms.IntegerField(min_value=1, label="Страница",required=False,initial=1)

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        if(len(args)>0):
            get_params=args[0]
            if('cat' in get_params):
                self.fields['cat']=forms.CharField(max_length=255,required=False,widget = forms.HiddenInput())
            if ('taxon' in get_params):
                self.fields['taxon'] = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput())