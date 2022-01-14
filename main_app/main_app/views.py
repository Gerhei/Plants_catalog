from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

# Create your views here.
def index(request):
    context={
        'title':'Главная страница'
    }
    return render(request,'main_app/index.html',context=context)

def pageNotFound(request,exception):
    return HttpResponseNotFound("Страница не найдена")