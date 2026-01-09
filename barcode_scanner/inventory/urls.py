from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Main buttons
    path('', views.home, name='home'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/admin/login/'), name='logout'),
    path('computer_list/', views.computer_list, name='computer_list'),

    # Computers
    path('save_barcode_computer/', views.save_barcode, name='save_barcode'),
    path('computer_form/<str:barcode>/', views.computer_form, name='computer_form'),
    path('scan-computer/', views.index, name='index'),
    path('computer/<str:pk>/', views.computers_form, name='computers_form'),
    path('delete_computer/<str:id>/', views.delete_computer, name='delete_pc'),
    path('add-computer/', views.add_computer, name='add_computer'),

    # Docking stations
    path('dockingstation-form/<str:barcode>/', views.dockingstation_form, name='dockingstation_form'),
    path('dockingstation/<str:pk>/', views.update_dockingstation_view, name='dockingstation_page'),
    path('save-barcode-dockingstation/', views.save_barcode_dockingstation, name='save_barcode_dockingstation'),
    path('scan-dockingstation/', views.scan_dockingstation, name='scan_dockingstation'),
    path('dockingStation-list/', views.dockingstation_list, name='dockingstation_list'),
    path('delete_dockingstation/<str:id>/', views.delete_dockingstation, name='delete_dockingstation'),
    path('add-dockingstation/', views.add_dockingstation, name='add_dockingstation'),

    # Monitors
    path('monitor-form/<str:barcode>/', views.monitor_form, name='monitor_form'),
    path('monitor/<str:pk>/', views.update_monitor_view, name='monitors_page'),
    path('save-barcode_monitor/', views.save_barcode_monitor, name='save_barcode_monitor'),
    path('scan-monitor/', views.scan_monitor, name='scan_monitor'),
    path('monitors-list/', views.monitor_list, name='monitors_list'),
    path('delete_monitor/<str:id>/', views.delete_monitor, name='delete_monitor'),
    path('add-monitor/', views.add_monitor, name='add_monitor'),

    # Printers
    path('printer/<str:pk>/', views.update_printer_view, name='printers_page'),
    path('add-printer/', views.add_printer, name='add_printer'),
    path('printers-list/', views.printer_list, name='printers_list'),
    path('delete_printer/<str:id>/', views.delete_printer, name='delete_printer'),
]