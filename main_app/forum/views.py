from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Count, F, Value, Q
from .models import *
# Create your views here.
def index(request):
    context={
        'title':'Форум',
    }
    return render(request,'forum/base.html',context=context)

class SuperSectionsListView(ListView):
    model=SuperSections
    template_name = 'forum/supersections_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title']="Форум"

        return context



class TopicsListView(ListView):
    model=Topics
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'slug_subsections' in self.kwargs:
            context['subsections'] = SubSections.objects.get(slug=self.kwargs['slug_subsections']).name
        else:
            context['subsections']="Все темы"
        return context

    def get_queryset(self):
        queryset=Topics.objects.prefetch_related('author')
        if 'slug_subsections' in self.kwargs:
            queryset=queryset.filter(sections__slug=self.kwargs['slug_subsections'])
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
