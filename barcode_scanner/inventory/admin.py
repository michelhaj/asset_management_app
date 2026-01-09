from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Computers, printers, monitors, docking_stations,
    AssetHistory, AssetAssignment, NotificationSetting
)


# =============================================================================
# Inline Admin Classes for Related Models
# =============================================================================

class MonitorsInline(admin.TabularInline):
    """Inline admin for monitors related to a computer."""
    model = monitors
    extra = 0
    fields = ['id', 'asset_tag', 'service_tag', 'make']
    readonly_fields = ['id']
    show_change_link = True


class DockingStationsInline(admin.TabularInline):
    """Inline admin for docking stations related to a computer."""
    model = docking_stations
    extra = 0
    fields = ['id', 'asset_tag', 'service_tag', 'make']
    readonly_fields = ['id']
    show_change_link = True


# =============================================================================
# ModelAdmin Classes
# =============================================================================

@admin.register(Computers)
class ComputersAdmin(admin.ModelAdmin):
    """Enhanced admin for Computers model with Jazzmin UI."""

    list_display = [
        'id', 'asset_tag', 'service_tag', 'computer_name',
        'department', 'user', 'make', 'model', 'status_badge', 'warranty_status',
        'get_monitors_count', 'get_docking_stations_count',
    ]

    list_filter = ['status', 'department', 'make', 'created_at']
    search_fields = ['asset_tag', 'service_tag', 'computer_name', 'user', 'make', 'model']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25
    list_max_show_all = 100
    filter_horizontal = ['printers']

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'asset_tag', 'service_tag', 'computer_name'),
            'classes': ('wide',),
        }),
        ('Assignment', {
            'fields': ('department', 'user', 'location'),
            'classes': ('wide',),
        }),
        ('Hardware Specifications', {
            'fields': ('make', 'model', 'storage', 'cpu', 'ram', 'printers'),
            'classes': ('wide', 'collapse'),
        }),
        ('Lifecycle', {
            'fields': ('status', 'purchase_date', 'warranty_expiry', 'purchase_cost'),
            'classes': ('wide',),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    inlines = [MonitorsInline, DockingStationsInline]

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

    def get_monitors_count(self, obj):
        """Get count of monitors connected to this computer."""
        count = obj.monitors.count()
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    get_monitors_count.short_description = 'Monitors'

    def get_docking_stations_count(self, obj):
        """Get count of docking stations connected to this computer."""
        count = obj.docking_stations.count()
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    get_docking_stations_count.short_description = 'Docking'


@admin.register(printers)
class PrintersAdmin(admin.ModelAdmin):
    """Enhanced admin for Printers model."""

    list_display = ['id', 'service_tag', 'make', 'description', 'status', 'location', 'get_computers_count']
    list_filter = ['status', 'make', 'created_at']
    search_fields = ['id', 'service_tag', 'make', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'service_tag'),
            'classes': ('wide',),
        }),
        ('Details', {
            'fields': ('make', 'description', 'status', 'location'),
            'classes': ('wide',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_computers_count(self, obj):
        """Get count of computers using this printer."""
        count = obj.computers.count()
        if count > 0:
            return format_html('<span style="color: blue; font-weight: bold;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    get_computers_count.short_description = 'Computers'


@admin.register(monitors)
class MonitorsAdmin(admin.ModelAdmin):
    """Enhanced admin for Monitors model."""

    list_display = ['id', 'asset_tag', 'service_tag', 'make', 'computer_link', 'status']
    list_filter = ['status', 'make', 'created_at']
    search_fields = ['id', 'asset_tag', 'service_tag', 'make', 'computer__asset_tag', 'computer__computer_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25
    autocomplete_fields = ['computer']

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'asset_tag', 'service_tag'),
            'classes': ('wide',),
        }),
        ('Details', {
            'fields': ('make', 'status'),
            'classes': ('wide',),
        }),
        ('Assignment', {
            'fields': ('computer',),
            'classes': ('wide',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def computer_link(self, obj):
        """Display computer as a clickable link."""
        if obj.computer:
            return format_html(
                '<a href="/admin/inventory/computers/{}/change/">{}</a>',
                obj.computer.id,
                obj.computer.asset_tag or obj.computer.id
            )
        return format_html('<span style="color: gray;">Not Assigned</span>')
    computer_link.short_description = 'Computer'
    computer_link.admin_order_field = 'computer__asset_tag'


@admin.register(docking_stations)
class DockingStationsAdmin(admin.ModelAdmin):
    """Enhanced admin for Docking Stations model."""

    list_display = ['id', 'asset_tag', 'service_tag', 'make', 'computer_link', 'status']
    list_filter = ['status', 'make', 'created_at']
    search_fields = ['id', 'asset_tag', 'service_tag', 'make', 'computer__asset_tag', 'computer__computer_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25
    autocomplete_fields = ['computer']

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'asset_tag', 'service_tag'),
            'classes': ('wide',),
        }),
        ('Details', {
            'fields': ('make', 'status'),
            'classes': ('wide',),
        }),
        ('Assignment', {
            'fields': ('computer',),
            'classes': ('wide',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def computer_link(self, obj):
        """Display computer as a clickable link."""
        if obj.computer:
            return format_html(
                '<a href="/admin/inventory/computers/{}/change/">{}</a>',
                obj.computer.id,
                obj.computer.asset_tag or obj.computer.id
            )
        return format_html('<span style="color: gray;">Not Assigned</span>')
    computer_link.short_description = 'Computer'
    computer_link.admin_order_field = 'computer__asset_tag'


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


# =============================================================================
# Admin Site Customization
# =============================================================================

admin.site.site_header = "Asset Management System"
admin.site.site_title = "Asset Management"
admin.site.index_title = "Welcome to Asset Management Dashboard"
