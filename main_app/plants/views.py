from django.shortcuts import render,get_object_or_404, redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.db.models import Count, F, Value, Q
from .models import *
from .forms import *
# Create your views here.
def random_plant(request):
    return redirect(Plants.objects.order_by('?').first(). get_absolute_url())

class PlantsListView(ListView):
    model=Plants
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if ('slug_cat' in self.kwargs):
            context['title'] = "Категория: "+Categories.objects.get(slug=self.kwargs['slug_cat']).name
        elif ('slug_taxon' in self.kwargs):
            taxon= Taxons.objects.get(slug=self.kwargs['slug_taxon'])
            context['title'] = taxon.get_order_display()+': '+taxon.name
        else:
            context['title'] = "Каталог растений"
        return context

    def get_queryset(self):
        queries=Q()
        if ('slug_cat' in self.kwargs):
            filter_val = self.kwargs['slug_cat']
            queries=Q(categories__slug=filter_val)
        elif ('slug_taxon' in self.kwargs):
            filter_val = self.kwargs['slug_taxon']
            queries = Q(taxons__slug=filter_val)
        if ('q' in self.request.GET):
            filter_q = self.request.GET['q'].lower()
            queries=queries & Q(name_lower__icontains=filter_q)

        queryset=Plants.objects.filter(queries)
        return queryset


class CategoriesListView(ListView):
    model=Categories
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Категории"
        return context

class TaxonsListView(ListView):
    model=Taxons
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = Taxons.objects.filter(order=self.kwargs['id_rang'])[0].get_order_display()
        return context

    def get_queryset(self):
        filter_val = self.kwargs['id_rang']
        new_context = Taxons.objects.filter(order=filter_val)
        return new_context

def taxons_rang(request):
    context={
        'title':'Таксоны',
        'rangs':Taxons.PRIORITIES
    }
    return render(request,'plants/taxons_rangs.html',context)

class PlantDetailView(DetailView):
    model = Plants