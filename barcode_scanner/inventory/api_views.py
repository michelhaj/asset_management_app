"""
REST API Views for the Asset Management System
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.utils import timezone

from .models import (
    Computers, printers, docking_stations, monitors,
    AssetHistory, AssetAssignment
)
from .serializers import (
    ComputerSerializer, ComputerListSerializer,
    PrinterSerializer, PrinterListSerializer,
    MonitorSerializer, MonitorListSerializer,
    DockingStationSerializer, DockingStationListSerializer,
    AssetHistorySerializer, AssetAssignmentSerializer,
    AssetAssignmentCreateSerializer, DashboardStatsSerializer
)


class StandardResultsPagination(PageNumberPagination):
    """Standard pagination for API results"""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class ComputerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for computers.

    list: Get all computers
    retrieve: Get a single computer
    create: Create a new computer
    update: Update a computer
    partial_update: Partially update a computer
    destroy: Delete a computer
    """
    queryset = Computers.objects.select_related().prefetch_related(
        'printers', 'monitors', 'docking_stations'
    ).all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'department', 'make', 'model']
    search_fields = ['asset_tag', 'service_tag', 'computer_name', 'user', 'make', 'model']
    ordering_fields = ['created_at', 'asset_tag', 'department', 'user']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ComputerListSerializer
        return ComputerSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get change history for a specific computer"""
        history = AssetHistory.objects.filter(
            asset_type='Computer',
            asset_id=pk
        ).order_by('-changed_at')
        serializer = AssetHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get computers grouped by department"""
        departments = Computers.objects.exclude(
            department__isnull=True
        ).exclude(
            department=''
        ).values('department').annotate(
            count=Count('id')
        ).order_by('-count')
        return Response(list(departments))


class PrinterViewSet(viewsets.ModelViewSet):
    """API endpoint for printers"""
    queryset = printers.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'make']
    search_fields = ['service_tag', 'make', 'description']
    ordering_fields = ['created_at', 'service_tag', 'make']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PrinterListSerializer
        return PrinterSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get change history for a specific printer"""
        history = AssetHistory.objects.filter(
            asset_type='Printer',
            asset_id=pk
        ).order_by('-changed_at')
        serializer = AssetHistorySerializer(history, many=True)
        return Response(serializer.data)


class MonitorViewSet(viewsets.ModelViewSet):
    """API endpoint for monitors"""
    queryset = monitors.objects.select_related('computer').all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'make', 'computer']
    search_fields = ['asset_tag', 'service_tag', 'make']
    ordering_fields = ['created_at', 'asset_tag', 'make']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return MonitorListSerializer
        return MonitorSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get change history for a specific monitor"""
        history = AssetHistory.objects.filter(
            asset_type='Monitor',
            asset_id=pk
        ).order_by('-changed_at')
        serializer = AssetHistorySerializer(history, many=True)
        return Response(serializer.data)


class DockingStationViewSet(viewsets.ModelViewSet):
    """API endpoint for docking stations"""
    queryset = docking_stations.objects.select_related('computer').all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'make', 'computer']
    search_fields = ['asset_tag', 'service_tag', 'make']
    ordering_fields = ['created_at', 'asset_tag', 'make']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return DockingStationListSerializer
        return DockingStationSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get change history for a specific docking station"""
        history = AssetHistory.objects.filter(
            asset_type='Docking Station',
            asset_id=pk
        ).order_by('-changed_at')
        serializer = AssetHistorySerializer(history, many=True)
        return Response(serializer.data)


class AssetHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for asset history (read-only)"""
    queryset = AssetHistory.objects.select_related('changed_by').order_by('-changed_at')
    serializer_class = AssetHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset_type', 'action', 'changed_by']
    search_fields = ['asset_id', 'asset_type']
    ordering_fields = ['changed_at', 'asset_type', 'action']
    ordering = ['-changed_at']


class AssetAssignmentViewSet(viewsets.ModelViewSet):
    """API endpoint for asset assignments"""
    queryset = AssetAssignment.objects.select_related(
        'assigned_by', 'approved_by'
    ).order_by('-assigned_date')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'asset_type', 'assigned_to']
    search_fields = ['asset_id', 'assigned_to', 'notes']
    ordering_fields = ['assigned_date', 'status', 'due_date']
    ordering = ['-assigned_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return AssetAssignmentCreateSerializer
        return AssetAssignmentSerializer

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user, status='pending')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an assignment"""
        assignment = self.get_object()
        if assignment.status != 'pending':
            return Response(
                {'error': 'Only pending assignments can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        assignment.status = 'approved'
        assignment.approved_by = request.user
        assignment.save()
        return Response({'status': 'Assignment approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an assignment"""
        assignment = self.get_object()
        if assignment.status != 'pending':
            return Response(
                {'error': 'Only pending assignments can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        assignment.status = 'rejected'
        assignment.approved_by = request.user
        assignment.save()
        return Response({'status': 'Assignment rejected'})

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """Check out an assignment"""
        assignment = self.get_object()
        if assignment.status != 'approved':
            return Response(
                {'error': 'Only approved assignments can be checked out'},
                status=status.HTTP_400_BAD_REQUEST
            )
        assignment.status = 'checked_out'
        assignment.save()
        return Response({'status': 'Asset checked out'})

    @action(detail=True, methods=['post'])
    def return_asset(self, request, pk=None):
        """Return an asset"""
        assignment = self.get_object()
        if assignment.status != 'checked_out':
            return Response(
                {'error': 'Only checked out assets can be returned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        assignment.status = 'returned'
        assignment.returned_date = timezone.now()
        assignment.save()
        return Response({'status': 'Asset returned'})


class DashboardViewSet(viewsets.ViewSet):
    """API endpoint for dashboard statistics"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get dashboard statistics"""
        stats = {
            'computer_count': Computers.objects.count(),
            'printer_count': printers.objects.count(),
            'monitor_count': monitors.objects.count(),
            'docking_station_count': docking_stations.objects.count(),
            'total_assets': (
                Computers.objects.count() +
                printers.objects.count() +
                monitors.objects.count() +
                docking_stations.objects.count()
            ),
            'pending_assignments': AssetAssignment.objects.filter(
                status='pending'
            ).count(),
        }

        # Status breakdown
        stats['status_breakdown'] = {
            'computers': list(Computers.objects.values('status').annotate(count=Count('id'))),
            'printers': list(printers.objects.values('status').annotate(count=Count('id'))),
            'monitors': list(monitors.objects.values('status').annotate(count=Count('id'))),
            'docking_stations': list(docking_stations.objects.values('status').annotate(count=Count('id'))),
        }

        # Recent activity
        recent_history = AssetHistory.objects.select_related(
            'changed_by'
        ).order_by('-changed_at')[:10]
        stats['recent_activity'] = AssetHistorySerializer(recent_history, many=True).data

        return Response(stats)
