from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.detail import DetailView,SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView,FormView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Value, Q
from .models import *
from .forms import *

# Create your views here.
def random_topic(request):
    return redirect(Topics.objects.order_by('?').first().get_absolute_url())

class SectionsListView(ListView):
    model=Sections
    template_name = 'forum/super_sections_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']="Форум"
        return context

    def get_queryset(self):
        queryset=Sections.objects.filter(super_sections__isnull=True)
        return queryset


class SectionDetailView(SingleObjectMixin, ListView):
    paginate_by = 10
    template_name = "forum/section_detail.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Sections.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']=self.object.name
        context['sections']=self.object.sections_set.all()
        context['super_section']=self.object.super_sections
        context['filter_form'] = FilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = self.object.topics_set.all()
        queries = Q()
        filter = self.request.GET
        if ('name' in filter):
            queries &= Q(name_lower__icontains=filter['name'].lower())
        if ('author' in filter):
            queries &= Q(author__username_lower__icontains=filter['author'].lower())
        queryset = queryset.filter(queries)

        if ('order' in filter and 'sort' in filter):
            order = ''
            if (filter['order'] == 'desc'):
                order = '-'
            queryset = queryset.order_by(f'{order}{filter["sort"]}')
        return queryset


class TopicsListView(ListView):
    model=Topics
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']="Все темы"
        context['filter_form'] = FilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset=Topics.objects.prefetch_related('author')
        queries = Q()
        filter = self.request.GET
        if ('name' in filter):
            queries &= Q(name_lower__icontains=filter['name'].lower())
        if ('author' in filter):
            queries &= Q(author__username_lower__icontains=filter['author'].lower())
        queryset = queryset.filter(queries)

        if ('order' in filter and 'sort' in filter):
            order = ''
            if (filter['order'] == 'desc'):
                order = '-'
            queryset = queryset.order_by(f'{order}{filter["sort"]}')
        return queryset


class PostsListView(ListView):
    model=Posts
    paginate_by = 10

    def post(self, request, *args, **kwargs):
        form = CreatePostForm(self.request.POST)
        topic = Topics.objects.get(slug=self.kwargs['slug_topic'])

        if form.is_valid():
            author=ForumUsers.objects.get(user=self.request.user)
            post = Posts.objects.create(text=form.cleaned_data['text'], topic=topic, post_type=1,author=author)
            post.save()
        redirect_to=reverse('topic', kwargs={'slug_topic':self.kwargs['slug_topic']})
        return redirect(f'{redirect_to}?page=last')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        topic=Topics.objects.get(slug=self.kwargs['slug_topic'])
        context['topic'] = topic
        context['super_section']=topic.sections

        if self.request.method == 'GET':
            context['form']=CreatePostForm()

        return context

    def get_queryset(self):
        queryset=Posts.objects.prefetch_related('author').filter(topic__slug=self.kwargs['slug_topic'])
        return queryset.order_by('post_type','time_create')


class TopicCreateView(LoginRequiredMixin,CreateView):
    model=Topics
    form_class = CreateTopicForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']='Создание темы'
        context['section']=Sections.objects.get(slug=self.kwargs['slug']).name

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'section': Sections.objects.get(slug=self.kwargs['slug']),
                       'author':self.request.user})
        return kwargs