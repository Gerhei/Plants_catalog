from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    context={
        'title':'Форум',
    }
    return render(request,'forum/index.html',context=context)
