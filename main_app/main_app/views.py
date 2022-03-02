from django.shortcuts import render,reverse,redirect
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseRedirect
from django.views.generic import CreateView
from django.contrib.auth import authenticate, login
from .forms import *

# Create your views here.
def index(request):
    return render(request,'main_app/index.html',context={'title':'Главная страница'})

class CreateUserView(CreateView):
    template_name = 'registration/user_form.html'
    form_class = MyUserForm
    success_url = 'profile'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return response

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        username = request.POST['username']
        password = request.POST['password2']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']='Регистрация'

        return context


def pageNotFound(request,exception):
    return HttpResponseNotFound("Страница не найдена")