from django.contrib import admin

from app.models import *

# Register your models here.
admin.site.register(Employee)


class TypeAdmin(admin.ModelAdmin):
    list_display = ('type_id', 'type_name')


admin.site.register(Type, TypeAdmin)


class ParentAdmin(admin.ModelAdmin):
    list_display = ('parent_id', 'parent_name')


admin.site.register(Parent, ParentAdmin)


class ProviderAdmin(admin.ModelAdmin):
    list_display = ('provider_id', 'provider_name', 'parent')


admin.site.register(Provider, ProviderAdmin)


class TimecodeAdmin(admin.ModelAdmin):
    list_display = ('time_code', 'time_code_desc', 'time_code_hours')


admin.site.register(Timecode, TimecodeAdmin)


class EngagementAdmin(admin.ModelAdmin):
    list_display = ('srg_id', 'start_date', 'fye', 'budget_amount', 'budget_hours', 'is_complete', 'complete_date',
                    'parent', 'provider', 'time_code', 'type')


admin.site.register(Engagement, EngagementAdmin)


class TimeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'engagement', 'date', 'hours', 'note')


admin.site.register(Time, TimeAdmin)
