from django.urls import path, include

from forum.views import *


urlpatterns = [
    path('', SectionsListView.as_view(), name="forum"),
    path('topics', TopicsListView.as_view(), name="all_topics"),
    path('random', random_topic, name='random_topic'),
    path('section/<slug:slug>', TopicsListView.as_view(), name="topics"),
    path('topic/<slug:slug>', TopicDetailView.as_view(), name="topic"),
    path('update-post/<int:pk>', PostUpdateView.as_view(), name="update_post"),
    path('delete-post/<int:pk>', PostDeleteView.as_view(), name="delete_post"),
    path('rate-post/<int:pk>', PostScoreChangeView.as_view(), name="rate_post"),
    path('create-post/topic-<int:pk>', PostCreateView.as_view(), name="create_post"),
    path('create-topic/section-<slug:slug>', TopicCreateView.as_view(), name="create_topic"),
    path('change-topic/<int:pk>', TopicUpdateView.as_view(), name="change_topic"),
    path('delete-topic/<int:pk>', TopicDeleteView.as_view(), name="delete_topic"),
    path('captcha/', include('captcha.urls'), name='captcha')
]
