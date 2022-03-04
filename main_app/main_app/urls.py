"""main_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main_app import settings
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls,name="admin"),
    path('', index,name="main"),
    path('plants/',include('plants.urls'),name="plants"),
    path('forum/',include('forum.urls'),name="forum"),
    path('news/',include('news.urls'),name="news"),
    path('accounts/profile/<slug:slug>',UserDetailView.as_view(),name="profile"),
    path('accounts/registration',CreateUserView.as_view(),name="registration"),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    import mimetypes

    mimetypes.add_type("application/javascript", ".js", True)

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns


handler404=pageNotFound