from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.detail import DetailView,SingleObjectMixin
from django.views.generic.list import ListView
from django.db.models import Count, F, Value, Q
from .models import *
# Create your views here.
def index(request):
    context={
        'title':'Форум',
    }
    return render(request,'forum/base.html',context=context)

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
    paginate_by = 2
    template_name = "forum/section_detail.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Sections.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']=self.object.name
        context['sections']=self.object.sections_set.all()
        return context

    def get_queryset(self):
        return self.object.topics_set.all()


class TopicsListView(ListView):
    model=Topics
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title']="Все темы"
        return context

    def get_queryset(self):
        queryset=Topics.objects.prefetch_related('author')
        return queryset


class PostsListView(ListView):
    model=Posts
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['topic'] = Topics.objects.get(slug=self.kwargs['slug_topic'])
        return context

    def get_queryset(self):
        queryset=Posts.objects.prefetch_related('author').filter(topic__slug=self.kwargs['slug_topic'])
        return queryset.order_by('post_type','time_create')
