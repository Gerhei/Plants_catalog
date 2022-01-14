from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    context={
        'title':'Новости',
    }
    return render(request,'news/index.html',context=context)

