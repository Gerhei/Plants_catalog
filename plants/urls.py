from django.urls import path

from .views import *


urlpatterns = [
    path('', PlantsListView.as_view(), name="plants"),
    path('taxons', taxons_rang, name="taxons"),
    path('taxons/<int:id_rang>', TaxonsListView.as_view(), name="taxons_rang"),
    path('categories', CategoriesListView.as_view(), name="categories"),
    path('random', random_plant, name='random_plant'),
    path('plant/<slug:slug>', PlantDetailView.as_view(), name='plant'),
]
