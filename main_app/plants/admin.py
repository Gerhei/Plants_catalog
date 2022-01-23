from django.contrib import admin
from .models import *
# Register your models here.
class PlantsAdmin(admin.ModelAdmin):
    list_display = ('id','name','time_create','time_update')
    list_display_links = ('id','name')
    search_fields = ('id','name')
    prepopulated_fields = {'slug':('name',)}

class DescriptionsAdmin(admin.ModelAdmin):
    list_display = ('id','category','plant','time_create','time_update')
    list_display_links = ('id','category','plant')
    search_fields = ('id','category','plant__name')

class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id','name','time_create','time_update')
    list_display_links = ('id','name')
    search_fields = ('id','name')
    prepopulated_fields = {'slug':('name',)}

class TaxonsAdmin(admin.ModelAdmin):
    list_display = ('id','rang','name','time_create','time_update')
    list_display_links = ('id','name')
    search_fields = ('id','rang','name')
    prepopulated_fields = {'slug':('rang','name')}

admin.site.register(Plants,PlantsAdmin)
admin.site.register(Descriptions,DescriptionsAdmin)
admin.site.register(Categories,CategoriesAdmin)
admin.site.register(Taxons,TaxonsAdmin)