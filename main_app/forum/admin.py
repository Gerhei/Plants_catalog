from django.contrib import admin
from .models import *

class SectionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order', 'super_sections')
    list_display_links = ('name',)
    list_filter = ('super_sections', 'order')
    search_fields = ('name_lower',)
    list_select_related = ('super_sections',)

    fields = ('name', 'super_sections', 'order', 'slug')
    readonly_fields = ('order', 'slug')


class TopicsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'sections', 'view_count', 'time_create')
    list_display_links = ('name',)
    list_filter = ('sections',)
    search_fields = ('name_lower', 'author__username_lower', 'id')
    list_select_related = ('author', 'sections')

    fields = ('name', 'sections', 'author', 'view_count', 'slug', 'time_create')
    readonly_fields = ('author', 'view_count', 'slug', 'time_create')


class PostsAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'author', 'post_type', 'topic', 'time_create', 'time_update')
    list_display_links = ('__str__',)
    list_filter = ('post_type',)
    search_fields = ('id', 'author__username_lower', 'topic__name')
    list_select_related = ('author', 'topic')

    fields = ('topic', 'text', 'post_type', 'author', 'time_create', 'time_update')
    readonly_fields = ('author', 'time_create', 'time_update')


class ForumUsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reputation')
    list_display_links = ('user',)
    search_fields = ('id', 'username_lower')
    list_select_related = ('user',)

    fields = ('user_image', 'about_user', 'reputation', 'slug')
    readonly_fields = ('about_user', 'reputation', 'slug')


class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'value_type', 'value')
    list_display_links = (('content_type', 'value_type'))
    list_filter = ('content_type', 'value_type')
    search_fields = ('id', 'user__username')
    list_select_related = ('user', 'content_type')

    fields = ('user', 'content_type', 'content_object', 'value_type', 'value')
    readonly_fields = ('user', 'content_type', 'content_object', 'value_type', 'value')


class AttachedFilesAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'time_create')
    search_fields = ('id', 'post__id')
    list_select_related = ('post',)

    fields = ('file', 'post')
    readonly_fields = ('post',)


admin.site.register(Sections, SectionsAdmin)
admin.site.register(Topics, TopicsAdmin)
admin.site.register(Posts, PostsAdmin)
admin.site.register(ForumUsers, ForumUsersAdmin)
admin.site.register(Statistics, StatisticsAdmin)
admin.site.register(AttachedFiles, AttachedFilesAdmin)