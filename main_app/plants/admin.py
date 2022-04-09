from django.contrib import admin
from .models import *


class PlantsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'time_create', 'time_update')
    list_display_links = ('name',)
    search_fields = ('name', 'name_lower', 'id')

    readonly_fields = ('slug', 'time_create', 'time_update')


class DescriptionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'plant', 'category', 'time_create', 'time_update')
    list_display_links = ('plant', 'category',)
    search_fields = ('category', 'plant__name', 'plant__name_lower', 'id')
    list_select_related = ('plant',)

    readonly_fields = ('time_create', 'time_update')


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name', 'name_lower', 'id')

    readonly_fields = ('slug', 'time_create', 'time_update')


class TaxonsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_order_display', 'time_create', 'time_update')
    list_display_links = ('name',)
    search_fields = ('name', 'id')

    readonly_fields = ('slug', 'time_create', 'time_update')


admin.site.register(Plants,PlantsAdmin)
admin.site.register(Descriptions,DescriptionsAdmin)
admin.site.register(Categories,CategoriesAdmin)
admin.site.register(Taxons,TaxonsAdmin)