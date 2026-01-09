"""
API URL Configuration for the Asset Management System
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'computers', api_views.ComputerViewSet, basename='computer')
router.register(r'printers', api_views.PrinterViewSet, basename='printer')
router.register(r'monitors', api_views.MonitorViewSet, basename='monitor')
router.register(r'docking-stations', api_views.DockingStationViewSet, basename='docking-station')
router.register(r'history', api_views.AssetHistoryViewSet, basename='history')
router.register(r'assignments', api_views.AssetAssignmentViewSet, basename='assignment')
router.register(r'dashboard', api_views.DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
