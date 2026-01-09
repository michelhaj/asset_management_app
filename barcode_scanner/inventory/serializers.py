"""
REST API Serializers for the Asset Management System
"""
from rest_framework import serializers
from .models import (
    Computers, printers, docking_stations, monitors,
    AssetHistory, AssetAssignment, AssetStatus
)


class ComputerSerializer(serializers.ModelSerializer):
    """Serializer for Computer model"""
    printers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=printers.objects.all(),
        required=False
    )

    class Meta:
        model = Computers
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ComputerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing computers"""
    class Meta:
        model = Computers
        fields = [
            'id', 'asset_tag', 'service_tag', 'computer_name',
            'department', 'user', 'make', 'model', 'status'
        ]


class PrinterSerializer(serializers.ModelSerializer):
    """Serializer for Printer model"""
    class Meta:
        model = printers
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PrinterListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing printers"""
    class Meta:
        model = printers
        fields = ['id', 'service_tag', 'make', 'description', 'status']


class MonitorSerializer(serializers.ModelSerializer):
    """Serializer for Monitor model"""
    computer_detail = ComputerListSerializer(source='computer', read_only=True)

    class Meta:
        model = monitors
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class MonitorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing monitors"""
    class Meta:
        model = monitors
        fields = ['id', 'asset_tag', 'service_tag', 'make', 'status', 'computer']


class DockingStationSerializer(serializers.ModelSerializer):
    """Serializer for Docking Station model"""
    computer_detail = ComputerListSerializer(source='computer', read_only=True)

    class Meta:
        model = docking_stations
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class DockingStationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing docking stations"""
    class Meta:
        model = docking_stations
        fields = ['id', 'asset_tag', 'service_tag', 'make', 'status', 'computer']


class AssetHistorySerializer(serializers.ModelSerializer):
    """Serializer for Asset History"""
    changed_by_username = serializers.CharField(
        source='changed_by.username',
        read_only=True,
        default=None
    )

    class Meta:
        model = AssetHistory
        fields = [
            'id', 'asset_type', 'asset_id', 'action',
            'changed_by', 'changed_by_username', 'changed_at',
            'old_values', 'new_values', 'ip_address'
        ]
        read_only_fields = fields


class AssetAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Asset Assignment"""
    assigned_by_username = serializers.CharField(
        source='assigned_by.username',
        read_only=True,
        default=None
    )
    approved_by_username = serializers.CharField(
        source='approved_by.username',
        read_only=True,
        default=None
    )

    class Meta:
        model = AssetAssignment
        fields = '__all__'
        read_only_fields = ['id', 'assigned_date', 'returned_date']


class AssetAssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Asset Assignments"""
    class Meta:
        model = AssetAssignment
        fields = ['asset_type', 'asset_id', 'assigned_to', 'due_date', 'notes']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    computer_count = serializers.IntegerField()
    printer_count = serializers.IntegerField()
    monitor_count = serializers.IntegerField()
    docking_station_count = serializers.IntegerField()
    total_assets = serializers.IntegerField()
    pending_assignments = serializers.IntegerField()


class BulkImportSerializer(serializers.Serializer):
    """Serializer for bulk import"""
    asset_type = serializers.ChoiceField(
        choices=['computers', 'printers', 'monitors', 'docking_stations']
    )
    csv_file = serializers.FileField()
