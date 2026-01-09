from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Computers, printers, monitors, docking_stations,
    AssetHistory, AssetAssignment, NotificationSetting
)


@admin.register(Computers)
class ComputersAdmin(admin.ModelAdmin):
    """Admin interface for Computers"""
    list_display = [
        'id', 'asset_tag', 'service_tag', 'computer_name',
        'department', 'user', 'make', 'model', 'status_badge', 'warranty_status'
    ]
    list_filter = ['status', 'department', 'make', 'created_at']
    search_fields = ['asset_tag', 'service_tag', 'computer_name', 'user', 'make', 'model']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'asset_tag', 'service_tag', 'computer_name')
        }),
        ('Assignment', {
            'fields': ('department', 'user', 'location')
        }),
        ('Hardware Details', {
            'fields': ('make', 'model', 'storage', 'cpu', 'ram', 'printers')
        }),
        ('Lifecycle', {
            'fields': ('status', 'purchase_date', 'warranty_expiry', 'purchase_cost')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'retired': 'gray',
            'repair': 'orange',
            'disposed': 'red',
            'available': 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def warranty_status(self, obj):
        if not obj.warranty_expiry:
            return '-'
        from django.utils import timezone
        today = timezone.now().date()
        if obj.warranty_expiry < today:
            return format_html('<span style="color: red;">Expired</span>')
        days_left = (obj.warranty_expiry - today).days
        if days_left <= 30:
            return format_html('<span style="color: orange;">{} days left</span>', days_left)
        return format_html('<span style="color: green;">{} days left</span>', days_left)
    warranty_status.short_description = 'Warranty'


@admin.register(printers)
class PrintersAdmin(admin.ModelAdmin):
    """Admin interface for Printers"""
    list_display = ['id', 'service_tag', 'make', 'description', 'status', 'location']
    list_filter = ['status', 'make', 'created_at']
    search_fields = ['service_tag', 'make', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(monitors)
class MonitorsAdmin(admin.ModelAdmin):
    """Admin interface for Monitors"""
    list_display = ['id', 'asset_tag', 'service_tag', 'make', 'computer', 'status']
    list_filter = ['status', 'make', 'created_at']
    search_fields = ['asset_tag', 'service_tag', 'make']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    autocomplete_fields = ['computer']


@admin.register(docking_stations)
class DockingStationsAdmin(admin.ModelAdmin):
    """Admin interface for Docking Stations"""
    list_display = ['id', 'asset_tag', 'service_tag', 'make', 'computer', 'status']
    list_filter = ['status', 'make', 'created_at']
    search_fields = ['asset_tag', 'service_tag', 'make']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    autocomplete_fields = ['computer']


@admin.register(AssetHistory)
class AssetHistoryAdmin(admin.ModelAdmin):
    """Admin interface for Asset History (read-only audit log)"""
    list_display = ['id', 'asset_type', 'asset_id', 'action', 'changed_by', 'changed_at', 'ip_address']
    list_filter = ['asset_type', 'action', 'changed_at']
    search_fields = ['asset_id', 'asset_type']
    readonly_fields = [
        'id', 'asset_type', 'asset_id', 'action', 'changed_by',
        'changed_at', 'old_values', 'new_values', 'ip_address'
    ]
    ordering = ['-changed_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):
    """Admin interface for Asset Assignments"""
    list_display = [
        'id', 'asset_type', 'asset_id', 'assigned_to',
        'status', 'assigned_by', 'assigned_date'
    ]
    list_filter = ['status', 'asset_type', 'assigned_date']
    search_fields = ['asset_id', 'assigned_to']
    readonly_fields = ['id', 'assigned_date', 'returned_date']
    ordering = ['-assigned_date']

    fieldsets = (
        ('Asset Information', {
            'fields': ('asset_type', 'asset_id')
        }),
        ('Assignment Details', {
            'fields': ('assigned_to', 'assigned_by', 'approved_by', 'status')
        }),
        ('Dates', {
            'fields': ('assigned_date', 'due_date', 'returned_date')
        }),
        ('Additional Info', {
            'fields': ('notes', 'digital_signature'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    """Admin interface for Notification Settings"""
    list_display = [
        'user', 'warranty_reminder_days', 'email_on_assignment',
        'email_on_warranty_expiry', 'daily_summary', 'weekly_summary'
    ]
    list_filter = ['email_on_assignment', 'email_on_warranty_expiry', 'daily_summary']
    search_fields = ['user__username', 'user__email']


# Customize admin site
admin.site.site_header = 'Asset Management System'
admin.site.site_title = 'Asset Management'
admin.site.index_title = 'Administration Dashboard'
