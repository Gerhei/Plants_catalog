from django.contrib import admin
from .models import *
# Register your models here.
class PlantsAdmin(admin.ModelAdmin):
    list_display = ('id','name','time_create','time_update')
    list_display_links = ('id','name')
    search_fields = ('id','name')

class DescriptionsAdmin(admin.ModelAdmin):
    list_display = ('id','category','plant','time_create','time_update')
    list_display_links = ('id','category','plant')
    search_fields = ('id','category','plant','text')

class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id','name','time_create','time_update')
    list_display_links = ('id','name')
    search_fields = ('id','name')

class TaxonsAdmin(admin.ModelAdmin):
    list_display = ('id','name','time_create','time_update')
    list_display_links = ('id','name')
    search_fields = ('id','name')

admin.site.register(Plants,PlantsAdmin)
admin.site.register(Descriptions,DescriptionsAdmin)
admin.site.register(Categories,CategoriesAdmin)
admin.site.register(Taxons,TaxonsAdmin)