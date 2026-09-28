from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from .models import (
    Machine,
    MachineSubscription,
    CameraFeed,
    Zone,
    Line,
    AIModel,
    CameraAIModel
)

# Unregister unnecessary models
admin.site.unregister(Group)

# Custom admin classes for Camera inlines
class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 1

class LineInline(admin.TabularInline):
    model = Line
    extra = 1

class CameraAIModelInline(admin.TabularInline):
    model = CameraAIModel
    extra = 1

# Custom admin classes for Machine inlines
class MachineSubscriptionInline(admin.TabularInline):
    model = MachineSubscription
    extra = 1
    readonly_fields = ('license_key',)

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('machine_name', 'machine_code', 'machine_id', 'country', 'state', 'city', 'is_active')
    list_filter = ('is_active', 'country', 'state', 'city')
    search_fields = ('machine_name', 'machine_code', 'machine_id')
    date_hierarchy = 'created_at'
    inlines = [MachineSubscriptionInline]

@admin.register(MachineSubscription)
class MachineSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('machine', 'license_key', 'start_date', 'end_date', 'subscription_type', 'is_active')
    list_filter = ('is_active', 'subscription_type', 'start_date', 'end_date')
    search_fields = ('machine__machine_name', 'license_key')
    date_hierarchy = 'created_at'
    readonly_fields = ('license_key',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('machine',)
        return self.readonly_fields

@admin.register(CameraFeed)
class CameraFeedAdmin(admin.ModelAdmin):
    list_display = ('machine', 'camera_name', 'camera_type', 'is_active', 'zone_count', 'line_count', 'ai_model_count')
    list_filter = ('is_active', 'camera_type', 'machine')
    search_fields = ('camera_name', 'machine__machine_name')
    date_hierarchy = 'created_at'
    inlines = [ZoneInline, LineInline, CameraAIModelInline]

    def zone_count(self, obj):
        return obj.zones.count()
    zone_count.short_description = 'Zones'

    def line_count(self, obj):
        return obj.lines.count()
    line_count.short_description = 'Lines'

    def ai_model_count(self, obj):
        return obj.ai_models.count()
    ai_model_count.short_description = 'AI Models'

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'model_type')
    list_filter = ('model_type',)
    search_fields = ('name', 'version', 'model_type')
    date_hierarchy = 'created_at'

# Customize the admin site header and title
admin.site.site_header = 'LPG Vending Machine Administration'
admin.site.site_title = 'LPG Vending Machine Admin'
admin.site.index_title = 'Administration' 