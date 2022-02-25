from django import forms
from .models import *

class CreateTopicForm(forms.ModelForm):
    text=forms.CharField(label="Текст сообщения",widget=forms.Textarea())

    class Meta:
        model = Topics
        fields = ['name','text']
        
    def save(self):
        # add author to topic and to post
        topic=super(CreateTopicForm, self).save()
        post=Posts(text=self.cleaned_data['text'],post_type=0,topic=topic)
        post.save()
        return topic