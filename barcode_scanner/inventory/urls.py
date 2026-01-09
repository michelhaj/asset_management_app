from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ==================== Main Pages ====================
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

    # ==================== Computers ====================
    path('computer_list/', views.computer_list, name='computer_list'),
    path('save_barcode_computer/', views.save_barcode, name='save_barcode'),
    path('computer_form/<str:barcode>/', views.computer_form, name='computer_form'),
    path('scan-computer/', views.index, name='index'),
    path('computer/<str:pk>/', views.computers_form, name='computers_form'),
    path('delete_computer/<str:id>/', views.delete_computer, name='delete_pc'),
    path('add-computer/', views.add_computer, name='add_computer'),

    # ==================== Docking Stations ====================
    path('dockingstation-form/<str:barcode>/', views.dockingtation_form, name='dockingstation_form'),
    path('dockingstation/<str:pk>/', views.update_dockingstation_view, name='dockingstation_page'),
    path('save-barcode-dockingstation/', views.save_barcode_dockingstation, name='save_barcode_dockingstation'),
    path('scan-dockingstation/', views.scan_dockingstation, name='scan_dockingstation'),
    path('dockingStation-list/', views.dockingstation_list, name='dockingstation_list'),
    path('delete_dockingstation/<str:id>/', views.delete_dockingstation, name='delete_dockingstation'),
    path('add-dockingstation/', views.add_dockingstation, name='add_dockingstation'),

    # ==================== Monitors ====================
    path('monitor-form/<str:barcode>/', views.monitor_form, name='monitor_form'),
    path('monitor/<str:pk>/', views.update_monitor_view, name='monitors_page'),
    path('save-barcode_monitor/', views.save_barcode_monitor, name='save_barcode_monitor'),
    path('scan-monitor/', views.scan_mointor, name='scan_monitor'),
    path('monitors-list/', views.monitor_list, name='monitors_list'),
    path('delete_monitor/<str:id>/', views.delete_monitor, name='delete_monitor'),
    path('add-monitor/', views.add_monitor, name='add_monitor'),

    # ==================== Printers ====================
    path('printer/<str:pk>/', views.update_printer_view, name='printers_page'),
    path('add-printer/', views.add_printer, name='add_printer'),
    path('printers-list/', views.printer_list, name='printers_list'),
    path('delete_prinet/<str:id>/', views.delete_printer, name='delete_printer'),

    # ==================== Bulk Import/Export ====================
    path('bulk-import/', views.bulk_import, name='bulk_import'),
    path('export/computers/csv/', views.export_computers_csv, name='export_computers_csv'),
    path('export/printers/csv/', views.export_printers_csv, name='export_printers_csv'),
    path('export/monitors/csv/', views.export_monitors_csv, name='export_monitors_csv'),
    path('export/docking-stations/csv/', views.export_docking_stations_csv, name='export_docking_stations_csv'),
    path('import-template/<str:asset_type>/', views.import_template_csv, name='import_template_csv'),

    # ==================== QR Code Generation ====================
    path('qr/<str:asset_type>/<str:asset_id>/', views.generate_qr_code, name='generate_qr_code'),

    # ==================== Asset History ====================
    path('history/', views.asset_history, name='asset_history'),
    path('history/<str:asset_type>/', views.asset_history, name='asset_history_filtered'),
    path('history/<str:asset_type>/<str:asset_id>/', views.asset_history, name='asset_history_detail'),

    # ==================== Asset Assignments ====================
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:assignment_id>/approve/', views.approve_assignment, name='approve_assignment'),
    path('assignments/<int:assignment_id>/reject/', views.reject_assignment, name='reject_assignment'),
    path('assignments/<int:assignment_id>/checkout/', views.checkout_assignment, name='checkout_assignment'),
    path('assignments/<int:assignment_id>/return/', views.return_assignment, name='return_assignment'),
]
