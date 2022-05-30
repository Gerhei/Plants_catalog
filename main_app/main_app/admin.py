from django.contrib import admin
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission, ContentType
import pprint


class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return pprint.pformat(obj.get_decoded()).replace('\n', '<br>\n')

    _session_data.allow_tags=True
    list_display = ('session_key', '_session_data', 'expire_date')
    readonly_fields = ('session_data', 'session_key', 'expire_date', '_session_data',)
    ordering = ('-expire_date',)


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('object_repr', 'action_flag', 'user', 'action_time')
    list_filter = ('user', 'action_flag')
    search_fields = ('object_repr', 'action_flag', 'user', 'action_time')


class PermissionAdmin(admin.ModelAdmin):
    readonly_fields = ('name', 'content_type', 'codename')


class ContentTypeAdmin(admin.ModelAdmin):
    readonly_fields = ('app_label', 'model', 'name')


admin.site.register(Session, SessionAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(ContentType, ContentTypeAdmin)
