from django.contrib import admin
from django.urls import path, include
from forum.views import *

urlpatterns = [
    path('', index,name="forum"),
]