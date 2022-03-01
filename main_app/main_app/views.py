from django.shortcuts import render,reverse
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import CreateView
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    return render(request,'main_app/index.html',context={'title':'Главная страница'})

class CreateUserView(CreateView):
    model = User
    template_name = 'registration/user_form.html'
    fields = ['username','password']
    success_url = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']='Регистрация'

        return context

def pageNotFound(request,exception):
    return HttpResponseNotFound("Страница не найдена")