from django.contrib import admin
from django.urls import path, include
from forum.views import *

urlpatterns = [
    path('', SuperSectionsListView.as_view(),name="forum"),
    path('topics', TopicsListView.as_view(), name="all_topics"),
    path('<slug:slug_subsections>', TopicsListView.as_view(),name="topics"),
    path('topics/<slug:slug_topic>', PostsListView.as_view(),name="topic"),
    #path('accounts/<slug:slug>', index,name="user_profile"),
    # path('sections',View.as_view(),name="")
]