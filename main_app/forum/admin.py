from django.contrib import admin
from .models import *
# Register your models here.
class SectionsAdmin(admin.ModelAdmin):
    list_display = ('id','name','order','super_sections')
    readonly_fields=['slug','order']
    list_display_links = ('id','name')
    search_fields = ('order', 'name','name_lower')

class TopicsAdmin(admin.ModelAdmin):
    list_display = ('id','name','author','sections','time_create')
    readonly_fields=['slug']
    list_display_links = ('id','name')
    search_fields = ('name','name_lower','author','sections')

class PostsAdmin(admin.ModelAdmin):
    list_display = ('id','author','topic','time_create')
    readonly_fields = ['score']
    list_display_links = ('id','author')
    search_fields = ('author','topic')

class ForumUsersAdmin(admin.ModelAdmin):
    list_display = ('id','user','reputation')
    readonly_fields = ['slug']
    list_display_links = ('id', 'user')
    search_fields = ('username_lower','reputation')

admin.site.register(Sections,SectionsAdmin)
admin.site.register(Topics,TopicsAdmin)
admin.site.register(Posts,PostsAdmin)
admin.site.register(ForumUsers,ForumUsersAdmin)