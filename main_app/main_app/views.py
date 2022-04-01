from django.shortcuts import render,reverse,redirect
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseRedirect
from django.views.generic import CreateView,DetailView,UpdateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import *

# Create your views here.
def index(request):
    return render(request,'main_app/index.html',context={'title':'Главная страница'})

@login_required()
def registration_done(request):
    return redirect(reverse('profile',kwargs={'slug':request.forumuser.slug}))


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'registration/profile_form.html'

    def setup(self, request, *args, **kwargs):
        self.user = request.user
        self.forumuser = request.forumuser
        super(UpdateProfile, self).setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']='Редактирование профиля'
        context['current_image'] = self.forumuser.user_image.url

        return context

    def get_object(self):
        return self.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'].update({"about_user": self.forumuser.about_user,
                                  'user_image':self.forumuser.user_image})
        return kwargs

    def get_success_url(self):
        return self.forumuser.get_absolute_url()


class UserDetailView(DetailView):
    model = User
    slug_field = 'forumusers__slug'
    template_name = 'registration/user_detail.html'

    def get_object(self):
        obj = User.objects.select_related('forumusers').get(forumusers__slug=self.kwargs.get(self.slug_url_kwarg))
        return obj


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