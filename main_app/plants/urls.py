from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index,name="plants"),
    #path('taxons', index,name="taxons"),
    #path('categories', index,name="categories"),
    path('<slug:slug>',PlantDetailView.as_view(),name='plant'),
]
