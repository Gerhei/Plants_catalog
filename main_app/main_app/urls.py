from django.contrib import admin
from django.contrib.staticfiles import views
from django.contrib.flatpages import views
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve
from django.urls import path, include, re_path
from main_app import settings
from .views import *

urlpatterns = [
    path('', views.flatpage, {'url': '/'}, name='main'),
    path('admin/', admin.site.urls, name="admin"),
    path('plants/', include('plants.urls'), name="plants"),
    path('forum/', include('forum.urls'), name="forum"),
    path('news/', include('news.urls'), name="news"),
    path('accounts/profile/<slug:slug>', UserDetailView.as_view(), name="profile"),
    path('accounts/update-profile', UpdateProfile.as_view(), name='profile_update'),
    path('accounts/registration', CreateUserView.as_view(), name="registration"),
    path('accounts/registration/done', registration_done, name="registration_done"),
    path('accounts/', include('django.contrib.auth.urls')),
]

urlpatterns += i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
)

if settings.DEBUG:
    import debug_toolbar
    import mimetypes

    mimetypes.add_type("application/javascript", ".js", True)

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

handler404 = pageNotFound