from django.shortcuts import render,get_object_or_404
from django.views.generic.detail import *
from django.http import HttpResponse
from .models import *
# Create your views here.
def index(request):
    context={
        'title':'Каталог растений',
    }
    return render(request,'plants/index.html',context=context)

class PlantDetailView(DetailView):
    model = Plants

def show_record(request,slug):
    plant=get_object_or_404(Plants,slug=slug)
    context={
        'title':plant.name,
        'name':plant.name,
        'image_url':plant.image_url,
        'categories':plant.categories.all(),
        'taxons':plant.taxons.all(),
        'descriptions':plant.descriptions_set.all()
    }
    return render(request,'plants/plant.html',context=context)