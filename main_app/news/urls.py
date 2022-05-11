from django.contrib import admin
from django.urls import path, include
from news.views import *

urlpatterns = [
    path('', NewsListView.as_view(), name="news"),
    path('detailed/<slug:slug>', NewsDetailView.as_view(), name="detailed_news"),
    path('random', random_news, name='random_news'),
]