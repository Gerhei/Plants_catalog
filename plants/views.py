from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.translation import gettext as _
from django.db.models import Q

from .models import *
from .forms import *


def random_plant(request):
    return redirect(Plants.objects.order_by('?').first().get_absolute_url())


class PlantsListView(ListView):
    model = Plants
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = FilterForm(self.request.GET)

        try:
            if ('cat' in self.request.GET):
                context['title'] = _("Category") + ": " + \
                                   Categories.objects.get(slug=self.request.GET['cat']).name
                context['super_title'] = _('Categories')
                context['super_url'] = 'categories'

            elif ('taxon' in self.request.GET):
                taxon = Taxons.objects.get(slug=self.request.GET['taxon'])
                context['title'] = taxon.get_order_display()+': ' + taxon.name
                context['super_title'] = _('Taxons')
                context['super_url'] = 'taxons'

            else:
                context['title'] = _('Plant catalog')
                context['super_title'] = _('All plants')
                context['super_url'] = 'plants'
            return context
        except (Categories.DoesNotExist, Taxons.DoesNotExist) as ex:
            raise Http404

    def get_queryset(self):
        queries = Q()
        filter_params = self.request.GET

        if ('cat' in filter_params):
            queries &= Q(categories__slug=filter_params['cat'])
        if ('taxon' in filter_params):
            queries &= Q(taxons__slug=filter_params['taxon'])
        if('name' in filter_params):
            queries &= Q(name_lower__icontains=filter_params['name'].lower())

        queryset = Plants.objects.prefetch_related('descriptions_set').filter(queries)

        if ('order' in filter_params and 'sort' in filter_params):
            order = ''
            if(filter_params['order']=='desc'):
                order = '-'
            queryset = queryset.order_by(f'{order}{filter_params["sort"]}')
        return queryset


class CategoriesListView(ListView):
    model = Categories
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = FilterForm(self.request.GET)
        context['title'] = _("Categories")
        context['super_title'] = _('All categories')
        context['super_url'] = 'categories'

        return context

    def get_queryset(self):
        queries = Q()
        filter_params = self.request.GET
        if('name' in filter_params):
            queries &= Q(name_lower__icontains=filter_params['name'].lower())

        queryset = Categories.objects.filter(queries)
        if ('order' in filter_params and 'sort' in filter_params):
            order = ''
            if (filter_params['order'] == 'desc'):
                order = '-'
            queryset = queryset.order_by(f'{order}{filter_params["sort"]}')
        return queryset


class TaxonsListView(ListView):
    model = Taxons
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = Taxons.objects.filter(order=self.kwargs['id_rang'])
        if (len(title)==0):
            raise Http404
        context['title'] = title[0].get_order_display()
        context['super_title'] = _('Taxons')
        context['super_url'] = 'taxons'
        return context

    def get_queryset(self):
        rang = self.kwargs['id_rang']
        queries = Q(order=rang)
        queryset = Taxons.objects.filter(queries)
        return queryset


def taxons_rang(request):
    context= {
        'title': _('Taxons'),
        'rangs': PRIORITIES
    }
    return render(request, 'plants/taxons_rangs.html', context)


class PlantDetailView(DetailView):
    model = Plants

    def get_context_data(self, **kwargs):
        context = super(PlantDetailView, self).get_context_data()
        context['title'] = self.object.name
        return context
