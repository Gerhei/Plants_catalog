from django import forms
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField

from .models import *


order_choices = [('inc', _('Ascending')),
                 ('desc', _('Descending'))]

order_by = [('publication_date', _('By publication date')), ('title', _('Alphabetically'))]

YEARS = [year for year in range(2000, 2030)]


class FilterForm(forms.Form):
    title = forms.CharField(max_length=255, required=False, label=_("Title"))
    publication_date = forms.DateField(required=False,
                                       widget=forms.SelectDateWidget(years=YEARS),
                                       label=_("Publication date"))
    sort = forms.ChoiceField(choices=order_by, required=False, label=_("Sorting by"))
    order = forms.ChoiceField(choices=order_choices, required=False, label=_("Sorting by"))
    page = forms.IntegerField(min_value=1, required=False, initial=1, label=_("Page"))


class CreateCommentForm(forms.ModelForm):
    text = forms.CharField(max_length=1000,
                           widget = forms.Textarea,
                           label=_('Comment'))

    def __init__(self, news=None, user=None, *args, **kwargs):
        super(CreateCommentForm, self).__init__(*args, **kwargs)
        self.news = news
        if isinstance(user, User):
            self.user = user
        else:
            self.user = None
            self.fields['captcha'] = CaptchaField(label=
                                                  _("Enter to prove that you are not a robot"))

    def save(self):
        comment = super(CreateCommentForm, self).save(commit=False)
        comment.news = self.news
        comment.user = self.user
        comment.save()
        return comment

    class Meta:
        model = Comments
        fields = ('text',)
