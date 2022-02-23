from django.contrib import admin
from django.urls import path, include
from forum.views import *

urlpatterns = [
    path('', SectionsListView.as_view(),name="forum"),
    path('topics', TopicsListView.as_view(), name="all_topics"),
    path('random', random_topic, name='random_topic'),
    path('section/<slug:slug>', SectionDetailView.as_view(),name="topics"),
    path('topics/<slug:slug_topic>', PostsListView.as_view(),name="topic"),
    path('create/topic', TopicCreateView.as_view(),name="create_topic"),
    #path('accounts/<slug:slug>', index,name="user_profile"),
]