from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    #----------------------------main buttons---------------------------
    path('home/', views.home, name='home'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
     path('computer_list/', views.computer_list, name='computer_list'),

      #---------------------------computers-----------------------------

    path('save_barcode_computer/', views.save_barcode, name='save_barcode'),
    path('computer_form/<str:barcode>/', views.computer_form, name='computer_form'),
    # path('computer_form/', views.computer_form_manual, name='computer_form_add_manually'),
    path('', views.index, name='index'),
    path('computer/<str:pk>/', views.computers_form, name='computers_form'),
    path('delete_computer/<str:pk>/', views.delete_computer, name='delete_pc'),

    #--------------------------docking station-----------------------------
    path('dockingstation-form/<str:barcode>/', views.dockingtation_form, name='dockingstation_form'),
    path('dockingstation/<str:pk>/', views.update_dockingstation_view, name='dockingstation_page'),
    path('save-barcode-dockingstation/', views.save_barcode_dockingstation, name='save_barcode_dockingstation'),
    path('scan-dockingstation/', views.scan_dockingstation, name='scan_dockingstation'),
    path('dockingStation-list/', views.dockingstation_list, name='dockingstation_list'),
    path('delete_dockingstation/<str:pk>/', views.delete_dockingstation, name='delete_dockingstation'),


   
     #---------------------------monitors buttons--------------------------
    path('monitor-form/<str:barcode>/', views.monitor_form, name='monitor_form'),
    path('monitor/<str:pk>/', views.update_monitor_view, name='monitors_page'),
    path('save-barcode_monitor/', views.save_barcode_monitor, name='save_barcode_monitor'),
    path('scan-monitor/', views.scan_mointor, name='scan_monitor'),
    path('monitors-list/', views.monitor_list, name='monitors_list'),
    path('delete_monitor/<str:pk>/', views.delete_monitor, name='delete_monitor'),
    #---------------------------printer buttons--------------------------
    path('printer/<str:pk>/',views.update_printer_view , name='printers_page'),
     path('add-printer/',views.add_printer , name='add_printer'),
   path('printers-list/', views.printer_list, name='printers_list'),
   path('delete_prinet/<str:pk>/', views.delete_printer, name='delete_printer'),


]