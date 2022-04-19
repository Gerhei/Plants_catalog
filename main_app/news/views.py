from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden

from django.views.generic import ListView, DetailView

from .models import *


class NewsListView(ListView):
    model = News
    paginate_by =  10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Список новостей"
        return context

    def get_queryset(self):
        queryset = News.objects.filter(is_published=True)
        return queryset


class NewsDetailView(DetailView):
    model = News

    def get(self, request, *args, **kwargs):
        response = super(NewsDetailView, self).get(request, *args, **kwargs)
        if not self.object.is_published:
            return HttpResponseForbidden()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['object'].title
        return context