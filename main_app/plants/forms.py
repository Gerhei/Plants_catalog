from django import forms
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy
from .models import *


order_choices = [('inc', _('Ascending')),
                 ('desc', _('Descending'))]

order_by=[('name', _('Alphabetically'))]


class FilterForm(forms.Form):
    name = forms.CharField(max_length=255, required=False, label=_lazy("Name"))
    sort = forms.ChoiceField(choices=order_by, required=False, label=_lazy("Sorting by"))
    order = forms.ChoiceField(choices=order_choices, required=False, label=_lazy("Sorting by"))
    page = forms.IntegerField(min_value=1, required=False, initial=1, label=_lazy("Page"))

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        if len(args) > 0:
            get_params = args[0]
            # take this fields from GET parameters
            if('cat' in get_params):
                self.fields['cat'] = forms.CharField(max_length=255, required=False,
                                                     widget=forms.HiddenInput())
            if ('taxon' in get_params):
                self.fields['taxon'] = forms.CharField(max_length=255, required=False,
                                                       widget=forms.HiddenInput())
