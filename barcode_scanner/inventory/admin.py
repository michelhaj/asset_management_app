from django.contrib import admin
from django.utils.html import format_html
from .models import Computers, printers, monitors, docking_stations


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
    """Enhanced admin for Computers model."""

    list_display = [
        'id',
        'asset_tag',
        'service_tag',
        'computer_name',
        'user',
        'department',
        'make',
        'model',
        'cpu',
        'ram',
        'storage',
        'get_monitors_count',
        'get_docking_stations_count',
    ]

    list_filter = [
        'department',
        'make',
        'model',
        'cpu',
        'ram',
        'storage',
    ]

    search_fields = [
        'id',
        'asset_tag',
        'service_tag',
        'computer_name',
        'user',
        'department',
        'make',
        'model',
    ]

    list_per_page = 25
    list_max_show_all = 100

    ordering = ['asset_tag']

    filter_horizontal = ['printers']

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'asset_tag', 'service_tag'),
            'classes': ('wide',),
        }),
        ('Assignment', {
            'fields': ('computer_name', 'user', 'department'),
            'classes': ('wide',),
        }),
        ('Hardware Specifications', {
            'fields': ('make', 'model', 'cpu', 'ram', 'storage'),
            'classes': ('wide', 'collapse'),
        }),
        ('Connected Devices', {
            'fields': ('printers',),
            'classes': ('wide',),
        }),
    )

    inlines = [MonitorsInline, DockingStationsInline]

    def get_monitors_count(self, obj):
        """Get count of monitors connected to this computer."""
        count = obj.monitors.count()
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    get_monitors_count.short_description = 'Monitors'
    get_monitors_count.admin_order_field = 'monitors__count'

    def get_docking_stations_count(self, obj):
        """Get count of docking stations connected to this computer."""
        count = obj.docking_stations.count()
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    get_docking_stations_count.short_description = 'Docking Stations'
    get_docking_stations_count.admin_order_field = 'docking_stations__count'


@admin.register(printers)
class PrintersAdmin(admin.ModelAdmin):
    """Enhanced admin for Printers model."""

    list_display = [
        'id',
        'service_tag',
        'make',
        'description',
        'get_computers_count',
    ]

    list_filter = [
        'make',
    ]

    search_fields = [
        'id',
        'service_tag',
        'make',
        'description',
    ]

    list_per_page = 25
    ordering = ['service_tag']

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'service_tag'),
            'classes': ('wide',),
        }),
        ('Details', {
            'fields': ('make', 'description'),
            'classes': ('wide',),
        }),
    )

    def get_computers_count(self, obj):
        """Get count of computers using this printer."""
        count = obj.Computers.count()
        if count > 0:
            return format_html('<span style="color: blue; font-weight: bold;">{}</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    get_computers_count.short_description = 'Connected Computers'


@admin.register(monitors)
class MonitorsAdmin(admin.ModelAdmin):
    """Enhanced admin for Monitors model."""

    list_display = [
        'id',
        'asset_tag',
        'service_tag',
        'make',
        'computer_link',
    ]

    list_filter = [
        'make',
    ]

    search_fields = [
        'id',
        'asset_tag',
        'service_tag',
        'make',
        'computer__asset_tag',
        'computer__computer_name',
    ]

    list_per_page = 25
    ordering = ['asset_tag']

    autocomplete_fields = ['computer']

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'asset_tag', 'service_tag'),
            'classes': ('wide',),
        }),
        ('Details', {
            'fields': ('make',),
            'classes': ('wide',),
        }),
        ('Assignment', {
            'fields': ('computer',),
            'classes': ('wide',),
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

    list_display = [
        'id',
        'asset_tag',
        'service_tag',
        'make',
        'computer_link',
    ]

    list_filter = [
        'make',
    ]

    search_fields = [
        'id',
        'asset_tag',
        'service_tag',
        'make',
        'computer__asset_tag',
        'computer__computer_name',
    ]

    list_per_page = 25
    ordering = ['asset_tag']

    autocomplete_fields = ['computer']

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'asset_tag', 'service_tag'),
            'classes': ('wide',),
        }),
        ('Details', {
            'fields': ('make',),
            'classes': ('wide',),
        }),
        ('Assignment', {
            'fields': ('computer',),
            'classes': ('wide',),
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


# =============================================================================
# Admin Site Customization
# =============================================================================

admin.site.site_header = "Asset Management System"
admin.site.site_title = "Asset Management"
admin.site.index_title = "Welcome to Asset Management Dashboard"
