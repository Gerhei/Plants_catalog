from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import HttpResponse, Http404
from django.db.models import Count, F, Value, Q
from django.views.decorators.csrf import csrf_exempt
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

        form=FilterForm(self.request.GET)
        context['filter_form']=form

        try:
            if ('cat' in self.request.GET):
                context['title'] = "Категория: "+Categories.objects.get(slug=self.request.GET['cat']).name
                context['super_title'] = 'Категории'
                context['super_url']='categories'
            elif ('taxon' in self.request.GET):
                taxon= Taxons.objects.get(slug=self.request.GET['taxon'])
                context['title'] = taxon.get_order_display()+': '+taxon.name
                context['super_title'] = 'Таксоны'
                context['super_url'] = 'taxons'
            else:
                context['title'] = "Каталог растений"
                context['super_title'] = 'Все растения'
                context['super_url'] ='plants'
            return context
        except (Categories.DoesNotExist,Taxons.DoesNotExist) as ex:
            raise Http404


    def get_queryset(self):
        queries=Q()
        filter=self.request.GET

        if ('cat' in filter):
            queries&=Q(categories__slug=filter['cat'])
        if ('taxon' in filter):
            queries &= Q(taxons__slug=filter['taxon'])
        if('name' in filter):
            queries &= Q(name_lower__icontains=filter['name'].lower())

        queryset=Plants.objects.prefetch_related('descriptions_set').filter(queries)

        if ('order' in filter and 'sort' in filter):
            order=''
            if(filter['order']=='desc'):
                order='-'
            queryset=queryset.order_by(f'{order}{filter["sort"]}')
        return queryset


class CategoriesListView(ListView):
    model=Categories
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form=FilterForm(self.request.GET)
        context['filter_form']=form

        context['title'] = "Категории"
        context['super_title'] = 'Все категории'
        context['super_url'] = 'categories'
        return context

    def get_queryset(self):
        queries=Q()
        filter = self.request.GET
        if('name' in filter):
            queries &= Q(name_lower__icontains=filter['name'].lower())

        queryset=Categories.objects.filter(queries)
        if ('order' in filter and 'sort' in filter):
            order = ''
            if (filter['order'] == 'desc'):
                order = '-'
            queryset = queryset.order_by(f'{order}{filter["sort"]}')
        return queryset

class TaxonsListView(ListView):
    model=Taxons
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = Taxons.objects.filter(order=self.kwargs['id_rang'])
        if (len(title)==0):
            raise Http404
        context['title']=title[0].get_order_display()
        context['super_title'] = 'Таксоны'
        context['super_url'] = 'taxons'
        return context

    def get_queryset(self):
        rang = self.kwargs['id_rang']
        queries = Q(order=rang)
        queryset = Taxons.objects.filter(queries)

        return queryset

def taxons_rang(request):
    context={
        'title':'Таксоны',
        'rangs':PRIORITIES
    }
    return render(request,'plants/taxons_rangs.html',context)

class PlantDetailView(DetailView):
    model = Plants