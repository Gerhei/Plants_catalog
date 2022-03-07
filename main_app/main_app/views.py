from django.shortcuts import render,reverse,redirect
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseRedirect
from django.views.generic import CreateView,DetailView,UpdateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import *

# Create your views here.
def index(request):
    return render(request,'main_app/index.html',context={'title':'Главная страница'})

@login_required()
def registration_done(request):
    return redirect(reverse('profile',kwargs={'slug':request.user.forumusers.slug}))


@login_required()
def update_email(request):
    context={}
    context['title']="Изменить почту"
    if request.method=="POST":
        form=EmailForm(request.POST)
        if form.is_valid():
            user=request.user
            user.email=form.cleaned_data['email']
            user.save()
            return redirect(reverse('profile',kwargs={'slug':user.forumusers.slug}), request)
        else:
            context['form']=form
    else:
        context['form']=EmailForm()

    return render(request,'registration/email_change.html',context=context)


class UserDetailView(DetailView):
    model = User
    slug_field = 'forumusers__slug'
    template_name = 'registration/user_detail.html'


class CreateUserView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = MyUserForm
    success_url = 'registration/done'

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