from django.contrib import admin
from .models import *


class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'publication_date', 'is_published')
    list_display_links = ('title',)
    list_filter = ('is_published',)
    search_fields = ('id', 'title', 'title_lower')

    #fields = ('title', 'publication_date', 'time_create', 'slug', 'is_published', 'source_url')
    #readonly_fields = ('publication_date', 'time_create', 'slug', 'source_url')
    fields = ('title', 'publication_date', 'time_create', 'slug', 'is_published', 'source_url', 'content')
    readonly_fields = ('time_create', 'slug')


class CommentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'news', 'user', 'time_create')
    list_display_links = ('news', 'user')
    search_fields = ('id', 'news__title', 'user__username')
    list_select_related = ('news', 'user')

    fields = ('user', 'news', 'time_create', 'text')
    #readonly_fields = ('user', 'news', 'publication_date', 'time_create', 'slug', 'source_url')
    readonly_fields = ('time_create',)


admin.site.register(News, NewsAdmin)
admin.site.register(Comments, CommentsAdmin)