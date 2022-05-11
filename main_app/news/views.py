from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden

from django.views.generic import ListView, DetailView
from django.db.models import Q

from .models import *
from .forms import *


def random_news(request):
    return redirect(News.objects.order_by('?').first().get_absolute_url())

class NewsListView(ListView):
    model = News
    paginate_by =  10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Список новостей"
        context['filter_form'] = FilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = News.objects.filter(is_published=True)
        queries = Q()
        filter = self.request.GET
        if ('title' in filter):
            queries &= Q(title_lower__icontains=filter['title'].lower())
        if 'publication_date_year' in filter and filter['publication_date_year']:
            queries &= Q(publication_date__year=filter['publication_date_year'])
        if 'publication_date_month' in filter and filter['publication_date_month']:
            queries &= Q(publication_date__month=filter['publication_date_month'])
        if 'publication_date_day' in filter and filter['publication_date_day']:
            queries &= Q(publication_date__day=filter['publication_date_day'])


        queryset = queryset.filter(queries)

        if ('order' in filter and 'sort' in filter):
            order = ''
            if (filter['order'] == 'desc'):
                order = '-'
            queryset = queryset.order_by(f'{order}{filter["sort"]}')
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