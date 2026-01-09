import csv
import io
import json
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import (
    Computers, printers, docking_stations, monitors,
    AssetHistory, AssetAssignment, AssetStatus
)
from .forms import computersForm, printersForm, docking_stationsForm, monitorsForm


# ==================== Permission Helpers ====================

def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff and user.is_superuser


def has_view_permission(user, model_name):
    """Check if user has view permission for a model"""
    if user.is_superuser:
        return True
    perm = f'inventory.can_view_{model_name}'
    return user.has_perm(perm)


def has_edit_permission(user, model_name):
    """Check if user has edit permission for a model"""
    if user.is_superuser:
        return True
    perm = f'inventory.can_edit_{model_name}'
    return user.has_perm(perm)


def has_delete_permission(user, model_name):
    """Check if user has delete permission for a model"""
    if user.is_superuser:
        return True
    perm = f'inventory.can_delete_{model_name}'
    return user.has_perm(perm)


def has_export_permission(user, model_name):
    """Check if user has export permission for a model"""
    if user.is_superuser:
        return True
    perm = f'inventory.can_export_{model_name}'
    return user.has_perm(perm)


# ==================== Pagination Helper ====================

def paginate_queryset(request, queryset, per_page=25):
    """Helper function to paginate a queryset"""
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page', 1)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return items


# ==================== Search Helper ====================

def apply_search_filters(queryset, request, search_fields):
    """Apply search filters to a queryset"""
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    department_filter = request.GET.get('department', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if search_query:
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f'{field}__icontains': search_query})
        queryset = queryset.filter(q_objects)

    if status_filter:
        queryset = queryset.filter(status=status_filter)

    if department_filter and hasattr(queryset.model, 'department'):
        queryset = queryset.filter(department__icontains=department_filter)

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass

    return queryset


# ==================== Dashboard View ====================

@user_passes_test(is_admin, login_url='/admin/login/')
def dashboard(request):
    """Dashboard with analytics and statistics"""
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_later = today + timedelta(days=7)

    # Asset counts
    computer_count = Computers.objects.count()
    printer_count = printers.objects.count()
    monitor_count = monitors.objects.count()
    docking_station_count = docking_stations.objects.count()
    total_assets = computer_count + printer_count + monitor_count + docking_station_count

    # Status breakdown
    status_counts = {
        'computers': Computers.objects.values('status').annotate(count=Count('id')),
        'printers': printers.objects.values('status').annotate(count=Count('id')),
        'monitors': monitors.objects.values('status').annotate(count=Count('id')),
        'docking_stations': docking_stations.objects.values('status').annotate(count=Count('id')),
    }

    # Department breakdown (for computers)
    department_counts = Computers.objects.exclude(
        department__isnull=True
    ).exclude(
        department=''
    ).values('department').annotate(count=Count('id')).order_by('-count')[:10]

    # Assets expiring warranty soon
    warranty_expiring = {
        'computers': Computers.objects.filter(
            warranty_expiry__gte=today,
            warranty_expiry__lte=seven_days_later
        ).count(),
        'printers': printers.objects.filter(
            warranty_expiry__gte=today,
            warranty_expiry__lte=seven_days_later
        ).count(),
        'monitors': monitors.objects.filter(
            warranty_expiry__gte=today,
            warranty_expiry__lte=seven_days_later
        ).count(),
        'docking_stations': docking_stations.objects.filter(
            warranty_expiry__gte=today,
            warranty_expiry__lte=seven_days_later
        ).count(),
    }

    # Recent activity
    recent_history = AssetHistory.objects.select_related('changed_by').order_by('-changed_at')[:10]

    # Recently added assets
    recent_computers = Computers.objects.order_by('-created_at')[:5]
    recent_monitors = monitors.objects.order_by('-created_at')[:5]

    # Pending assignments
    pending_assignments = AssetAssignment.objects.filter(status='pending').count()

    context = {
        'computer_count': computer_count,
        'printer_count': printer_count,
        'monitor_count': monitor_count,
        'docking_station_count': docking_station_count,
        'total_assets': total_assets,
        'status_counts': status_counts,
        'department_counts': list(department_counts),
        'warranty_expiring': warranty_expiring,
        'recent_history': recent_history,
        'recent_computers': recent_computers,
        'recent_monitors': recent_monitors,
        'pending_assignments': pending_assignments,
    }

    return render(request, 'dashboard.html', context)


# ==================== Home View ====================

@user_passes_test(is_admin, login_url='/admin/login/')
def home(request):
    """Home page with optimized computer list"""
    # Optimized query with select_related and prefetch_related
    computer_items = Computers.objects.select_related().prefetch_related(
        'printers', 'monitors', 'docking_stations'
    ).all()

    # Apply search filters
    search_fields = ['asset_tag', 'service_tag', 'computer_name', 'user', 'make', 'model', 'department']
    computer_items = apply_search_filters(computer_items, request, search_fields)

    # Paginate results
    computer_items = paginate_queryset(request, computer_items, per_page=20)

    # Get filter options for dropdowns
    statuses = AssetStatus.choices
    departments = Computers.objects.exclude(
        department__isnull=True
    ).exclude(
        department=''
    ).values_list('department', flat=True).distinct()

    context = {
        'computer_items': computer_items,
        'statuses': statuses,
        'departments': list(departments),
        'search_query': request.GET.get('q', ''),
        'status_filter': request.GET.get('status', ''),
        'department_filter': request.GET.get('department', ''),
    }

    return render(request, 'home.html', context)


# ==================== Computer Views ====================

@user_passes_test(is_admin, login_url='/admin/login/')
def index(request):
    """Barcode scanning page for computers"""
    return render(request, 'index.html')


@user_passes_test(is_admin, login_url='/admin/login/')
def save_barcode(request):
    """Save scanned barcode for computer"""
    if request.method == 'POST':
        barcode_data = request.POST.get('barcode_data', None)
        if barcode_data:
            computer, created = Computers.objects.get_or_create(asset_tag=barcode_data)
            if created:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Barcode saved successfully',
                    'new_item': True
                })
            else:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Barcode already exists',
                    'existing_item': True
                })
        else:
            return JsonResponse({'status': 'error', 'message': 'No barcode data received'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@user_passes_test(is_admin, login_url='/admin/login/')
def computer_form(request, barcode):
    """Computer form from barcode scan"""
    computer = get_object_or_404(Computers, asset_tag=barcode)
    url = reverse('computer_form', kwargs={'barcode': barcode})

    if request.method == 'POST':
        form = computersForm(request.POST, instance=computer)
        if form.is_valid():
            form.save()
            messages.success(request, "Computer data has been saved.")
            return redirect('computer_list')
        else:
            messages.error(request, "Error saving computer data.")
    else:
        form = computersForm(instance=computer)

    return render(request, 'computer_form.html', {'form': form, 'url': url, 'pc': computer})


@user_passes_test(is_admin, login_url='/admin/login/')
def computers_form(request, pk):
    """Edit existing computer"""
    computer = get_object_or_404(Computers, id=pk)
    form = computersForm(instance=computer)

    if request.method == 'POST':
        form = computersForm(request.POST, instance=computer)
        if form.is_valid():
            form.save()
            messages.success(request, "Computer data has been updated.")
            return redirect('computer_list')

    return render(request, 'computer_form.html', {'form': form, 'pc': computer})


@user_passes_test(is_admin, login_url='/admin/login/')
def delete_computer(request, id):
    """Delete a computer"""
    computer = get_object_or_404(Computers, id=id)
    computer.delete()
    messages.success(request, "Computer has been deleted.")
    return redirect('computer_list')


@user_passes_test(is_admin, login_url='/admin/login/')
def add_computer(request):
    """Add new computer manually"""
    if request.method == 'POST':
        form = computersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Computer data has been added.')
            return redirect('home')
        else:
            messages.error(request, 'Error while adding computer data.')
            return redirect('add_computer')
    else:
        form = computersForm()

    return render(request, 'computer_form.html', {'form': form})


@user_passes_test(is_admin, login_url='/admin/login/')
def computer_list(request):
    """List all computers with pagination and search"""
    computer_items = Computers.objects.select_related().prefetch_related(
        'printers', 'monitors', 'docking_stations'
    ).all()

    # Apply search filters
    search_fields = ['asset_tag', 'service_tag', 'computer_name', 'user', 'make', 'model', 'department']
    computer_items = apply_search_filters(computer_items, request, search_fields)

    # Paginate
    computer_items = paginate_queryset(request, computer_items, per_page=25)

    statuses = AssetStatus.choices

    return render(request, 'computer_list.html', {
        'computer_items': computer_items,
        'statuses': statuses,
        'search_query': request.GET.get('q', ''),
    })


# ==================== Printer Views ====================

@user_passes_test(is_admin, login_url='/admin/login/')
def update_printer_view(request, pk):
    """Update printer"""
    printer = get_object_or_404(printers, id=pk)
    printerform = printersForm(instance=printer)
    mydict = {'form': printerform, 'printers': printer}

    if request.method == 'POST':
        printerform = printersForm(request.POST, instance=printer)
        if printerform.is_valid():
            printerform.save()
            messages.success(request, 'Printer data has been updated.')
            return redirect('printers_list')
        else:
            messages.error(request, 'Error while updating printer data.')
            return redirect('printers_list')

    return render(request, 'printersform.html', context=mydict)


@user_passes_test(is_admin, login_url='/admin/login/')
def delete_printer(request, id):
    """Delete printer"""
    printer = get_object_or_404(printers, id=id)
    printer.delete()
    messages.success(request, "Printer has been deleted.")
    return redirect('printers_list')


@user_passes_test(is_admin, login_url='/admin/login/')
def add_printer(request):
    """Add new printer"""
    if request.method == 'POST':
        printerform = printersForm(request.POST)
        if printerform.is_valid():
            printerform.save()
            messages.success(request, 'Printer data has been added.')
            return redirect('home')
        else:
            messages.error(request, 'Error while adding printer.')
            return redirect('add_printer')
    else:
        printerform = printersForm()

    return render(request, 'add_printer.html', {'form': printerform})


@user_passes_test(is_admin, login_url='/admin/login/')
def printer_list(request):
    """List all printers with pagination and search"""
    printer_items = printers.objects.all()

    # Apply search filters
    search_fields = ['service_tag', 'make', 'description']
    printer_items = apply_search_filters(printer_items, request, search_fields)

    # Paginate
    printer_items = paginate_queryset(request, printer_items, per_page=25)

    statuses = AssetStatus.choices

    return render(request, 'printer_list.html', {
        'printer_items': printer_items,
        'statuses': statuses,
        'search_query': request.GET.get('q', ''),
    })


# ==================== Monitor Views ====================

@user_passes_test(is_admin, login_url='/admin/login/')
def update_monitor_view(request, pk):
    """Update monitor"""
    monitor = get_object_or_404(monitors, id=pk)
    monitorform = monitorsForm(instance=monitor)
    mydict = {'form': monitorform, 'monitor': monitor}

    if request.method == 'POST':
        monitorform = monitorsForm(request.POST, instance=monitor)
        if monitorform.is_valid():
            monitorform.save()
            messages.success(request, 'Monitor data has been updated.')
        else:
            messages.error(request, 'Error updating monitor.')

    return render(request, 'monitors_form.html', context=mydict)


@user_passes_test(is_admin, login_url='/admin/login/')
def scan_mointor(request):
    """Scan monitor barcode"""
    return render(request, 'scan_monitor.html')


@user_passes_test(is_admin, login_url='/admin/login/')
def save_barcode_monitor(request):
    """Save scanned barcode for monitor"""
    if request.method == 'POST':
        barcode_data = request.POST.get('barcode_data', None)
        if barcode_data:
            monitor, created = monitors.objects.get_or_create(asset_tag=barcode_data)
            if created:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Barcode saved successfully',
                    'new_item': True
                })
            else:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Barcode already exists',
                    'existing_item': True
                })
        else:
            return JsonResponse({'status': 'error', 'message': 'No barcode data received'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@user_passes_test(is_admin, login_url='/admin/login/')
def monitor_form(request, barcode):
    """Monitor form from barcode scan"""
    monitor = get_object_or_404(monitors, asset_tag=barcode)
    url = reverse('monitor_form', kwargs={'barcode': barcode})

    if request.method == 'POST':
        form = monitorsForm(request.POST, instance=monitor)
        if form.is_valid():
            form.save()
            messages.success(request, "Monitor data has been saved.")
            return redirect('monitors_list')
        else:
            messages.error(request, "Error saving monitor data.")
    else:
        form = monitorsForm(instance=monitor)

    return render(request, 'monitors_form.html', {'form': form, 'url': url, 'monitor': monitor})


@user_passes_test(is_admin, login_url='/admin/login/')
def add_monitor(request):
    """Add new monitor manually"""
    if request.method == 'POST':
        monitorform = monitorsForm(request.POST)
        if monitorform.is_valid():
            monitorform.save()
            messages.success(request, 'Monitor data has been added.')
            return redirect('home')
        else:
            messages.error(request, 'Error while adding monitor data.')
            return redirect('add_monitor')
    else:
        monitorform = monitorsForm()

    return render(request, 'monitors_form.html', {'form': monitorform})


@user_passes_test(is_admin, login_url='/admin/login/')
def delete_monitor(request, id):
    """Delete monitor"""
    monitor = get_object_or_404(monitors, id=id)
    monitor.delete()
    messages.success(request, "Monitor has been deleted.")
    return redirect('monitors_list')


@user_passes_test(is_admin, login_url='/admin/login/')
def monitor_list(request):
    """List all monitors with pagination and search"""
    monitor_items = monitors.objects.select_related('computer').all()

    # Apply search filters
    search_fields = ['asset_tag', 'service_tag', 'make']
    monitor_items = apply_search_filters(monitor_items, request, search_fields)

    # Paginate
    monitor_items = paginate_queryset(request, monitor_items, per_page=25)

    statuses = AssetStatus.choices

    return render(request, 'monitor_list.html', {
        'monitor_items': monitor_items,
        'statuses': statuses,
        'search_query': request.GET.get('q', ''),
    })


# ==================== Docking Station Views ====================

@user_passes_test(is_admin, login_url='/admin/login/')
def update_dockingstation_view(request, pk):
    """Update docking station"""
    dockingstation = get_object_or_404(docking_stations, id=pk)
    dockingstationform = docking_stationsForm(instance=dockingstation)
    mydict = {'form': dockingstationform, 'dockingstation': dockingstation}

    if request.method == 'POST':
        dockingstationform = docking_stationsForm(request.POST, instance=dockingstation)
        if dockingstationform.is_valid():
            dockingstationform.save()
            messages.success(request, 'Docking station data has been updated.')
            return redirect('dockingstation_list')
        else:
            messages.error(request, 'Error updating docking station.')
            return redirect('home')

    return render(request, 'docking_stations_form.html', context=mydict)


@user_passes_test(is_admin, login_url='/admin/login/')
def delete_dockingstation(request, id):
    """Delete docking station"""
    dockingstation = get_object_or_404(docking_stations, id=id)
    dockingstation.delete()
    messages.success(request, "Docking station has been deleted.")
    return redirect('dockingstation_list')


@user_passes_test(is_admin, login_url='/admin/login/')
def scan_dockingstation(request):
    """Scan docking station barcode"""
    return render(request, 'scan_docking_station.html')


@user_passes_test(is_admin, login_url='/admin/login/')
def save_barcode_dockingstation(request):
    """Save scanned barcode for docking station"""
    if request.method == 'POST':
        barcode_data = request.POST.get('barcode_data', None)
        if barcode_data:
            dockingstation, created = docking_stations.objects.get_or_create(asset_tag=barcode_data)
            if created:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Barcode saved successfully',
                    'new_item': True
                })
            else:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Barcode already exists',
                    'existing_item': True
                })
        else:
            return JsonResponse({'status': 'error', 'message': 'No barcode data received'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@user_passes_test(is_admin, login_url='/admin/login/')
def dockingtation_form(request, barcode):
    """Docking station form from barcode scan"""
    dockingstation = get_object_or_404(docking_stations, asset_tag=barcode)
    url = reverse('dockingstation_form', kwargs={'barcode': barcode})

    if request.method == 'POST':
        form = docking_stationsForm(request.POST, instance=dockingstation)
        if form.is_valid():
            form.save()
            messages.success(request, "Docking station data has been saved.")
            return redirect('dockingstation_list')
        else:
            messages.error(request, "Error saving docking station data.")
    else:
        form = docking_stationsForm(instance=dockingstation)

    return render(request, 'docking_stations_form.html', {'form': form, 'url': url, 'dockingstation': dockingstation})


@user_passes_test(is_admin, login_url='/admin/login/')
def add_dockingstation(request):
    """Add new docking station manually"""
    if request.method == 'POST':
        dockingstationform = docking_stationsForm(request.POST)
        if dockingstationform.is_valid():
            dockingstationform.save()
            messages.success(request, 'Docking station data has been added.')
            return redirect('home')
        else:
            messages.error(request, 'Error while adding docking station data.')
            return redirect('add_dockingstation')
    else:
        dockingstationform = docking_stationsForm()

    return render(request, 'docking_stations_form.html', {'form': dockingstationform})


@user_passes_test(is_admin, login_url='/admin/login/')
def dockingstation_list(request):
    """List all docking stations with pagination and search"""
    dockingstation_items = docking_stations.objects.select_related('computer').all()

    # Apply search filters
    search_fields = ['asset_tag', 'service_tag', 'make']
    dockingstation_items = apply_search_filters(dockingstation_items, request, search_fields)

    # Paginate
    dockingstation_items = paginate_queryset(request, dockingstation_items, per_page=25)

    statuses = AssetStatus.choices

    return render(request, 'docking_station_list.html', {
        'dockingstation_items': dockingstation_items,
        'statuses': statuses,
        'search_query': request.GET.get('q', ''),
    })


# ==================== Bulk Import/Export Views ====================

@user_passes_test(is_admin, login_url='/admin/login/')
def export_computers_csv(request):
    """Export computers to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="computers_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Asset Tag', 'Service Tag', 'Computer Name', 'Department',
        'User', 'Make', 'Model', 'Storage', 'CPU', 'RAM', 'Status',
        'Location', 'Purchase Date', 'Warranty Expiry', 'Purchase Cost', 'Notes'
    ])

    computers = Computers.objects.all()
    for computer in computers:
        writer.writerow([
            computer.id, computer.asset_tag, computer.service_tag,
            computer.computer_name, computer.department, computer.user,
            computer.make, computer.model, computer.storage, computer.cpu,
            computer.ram, computer.status, computer.location,
            computer.purchase_date, computer.warranty_expiry,
            computer.purchase_cost, computer.notes
        ])

    return response


@user_passes_test(is_admin, login_url='/admin/login/')
def export_printers_csv(request):
    """Export printers to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="printers_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Service Tag', 'Make', 'Description', 'Status',
        'Location', 'Purchase Date', 'Warranty Expiry', 'Purchase Cost', 'Notes'
    ])

    printer_list = printers.objects.all()
    for printer in printer_list:
        writer.writerow([
            printer.id, printer.service_tag, printer.make, printer.description,
            printer.status, printer.location, printer.purchase_date,
            printer.warranty_expiry, printer.purchase_cost, printer.notes
        ])

    return response


@user_passes_test(is_admin, login_url='/admin/login/')
def export_monitors_csv(request):
    """Export monitors to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="monitors_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Asset Tag', 'Service Tag', 'Make', 'Computer ID', 'Status',
        'Location', 'Purchase Date', 'Warranty Expiry', 'Purchase Cost', 'Notes'
    ])

    monitor_list = monitors.objects.select_related('computer').all()
    for monitor in monitor_list:
        writer.writerow([
            monitor.id, monitor.asset_tag, monitor.service_tag, monitor.make,
            monitor.computer_id if monitor.computer else '',
            monitor.status, monitor.location, monitor.purchase_date,
            monitor.warranty_expiry, monitor.purchase_cost, monitor.notes
        ])

    return response


@user_passes_test(is_admin, login_url='/admin/login/')
def export_docking_stations_csv(request):
    """Export docking stations to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="docking_stations_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Asset Tag', 'Service Tag', 'Make', 'Computer ID', 'Status',
        'Location', 'Purchase Date', 'Warranty Expiry', 'Purchase Cost', 'Notes'
    ])

    ds_list = docking_stations.objects.select_related('computer').all()
    for ds in ds_list:
        writer.writerow([
            ds.id, ds.asset_tag, ds.service_tag, ds.make,
            ds.computer_id if ds.computer else '',
            ds.status, ds.location, ds.purchase_date,
            ds.warranty_expiry, ds.purchase_cost, ds.notes
        ])

    return response


@user_passes_test(is_admin, login_url='/admin/login/')
def import_template_csv(request, asset_type):
    """Download CSV import template"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{asset_type}_import_template.csv"'

    writer = csv.writer(response)

    if asset_type == 'computers':
        writer.writerow([
            'Asset Tag', 'Service Tag', 'Computer Name', 'Department',
            'User', 'Make', 'Model', 'Storage', 'CPU', 'RAM', 'Status',
            'Location', 'Purchase Date (YYYY-MM-DD)', 'Warranty Expiry (YYYY-MM-DD)',
            'Purchase Cost', 'Notes'
        ])
        writer.writerow([
            'COMP-001', 'SVC-001', 'DESKTOP-01', 'IT', 'John Doe',
            'Dell', 'OptiPlex 7090', '512GB SSD', 'Intel i7', '16GB',
            'active', 'Building A', '2024-01-15', '2027-01-15', '1500.00', 'Sample note'
        ])
    elif asset_type == 'printers':
        writer.writerow([
            'Service Tag', 'Make', 'Description', 'Status', 'Location',
            'Purchase Date (YYYY-MM-DD)', 'Warranty Expiry (YYYY-MM-DD)',
            'Purchase Cost', 'Notes'
        ])
        writer.writerow([
            'PRT-001', 'HP', 'LaserJet Pro M404n', 'active', 'Floor 2',
            '2024-01-15', '2027-01-15', '350.00', 'Sample note'
        ])
    elif asset_type == 'monitors':
        writer.writerow([
            'Asset Tag', 'Service Tag', 'Make', 'Status', 'Location',
            'Purchase Date (YYYY-MM-DD)', 'Warranty Expiry (YYYY-MM-DD)',
            'Purchase Cost', 'Notes'
        ])
        writer.writerow([
            'MON-001', 'SVC-MON-001', 'Dell P2419H', 'active', 'Building A',
            '2024-01-15', '2027-01-15', '250.00', 'Sample note'
        ])
    elif asset_type == 'docking_stations':
        writer.writerow([
            'Asset Tag', 'Service Tag', 'Make', 'Status', 'Location',
            'Purchase Date (YYYY-MM-DD)', 'Warranty Expiry (YYYY-MM-DD)',
            'Purchase Cost', 'Notes'
        ])
        writer.writerow([
            'DOCK-001', 'SVC-DOCK-001', 'Dell WD19', 'active', 'Building A',
            '2024-01-15', '2027-01-15', '200.00', 'Sample note'
        ])

    return response


@user_passes_test(is_admin, login_url='/admin/login/')
def bulk_import(request):
    """Bulk import assets from CSV"""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        asset_type = request.POST.get('asset_type')

        if not csv_file:
            messages.error(request, 'Please select a CSV file.')
            return redirect('bulk_import')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('bulk_import')

        try:
            decoded_file = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))

            success_count = 0
            error_count = 0
            errors = []

            for row_num, row in enumerate(reader, start=2):
                try:
                    if asset_type == 'computers':
                        Computers.objects.update_or_create(
                            asset_tag=row.get('Asset Tag', '').strip(),
                            defaults={
                                'service_tag': row.get('Service Tag', '').strip() or None,
                                'computer_name': row.get('Computer Name', '').strip() or None,
                                'department': row.get('Department', '').strip() or None,
                                'user': row.get('User', '').strip() or None,
                                'make': row.get('Make', '').strip() or None,
                                'model': row.get('Model', '').strip() or None,
                                'storage': row.get('Storage', '').strip() or None,
                                'cpu': row.get('CPU', '').strip() or None,
                                'ram': row.get('RAM', '').strip() or None,
                                'status': row.get('Status', 'active').strip() or 'active',
                                'location': row.get('Location', '').strip() or None,
                                'notes': row.get('Notes', '').strip() or None,
                            }
                        )
                    elif asset_type == 'printers':
                        printers.objects.update_or_create(
                            service_tag=row.get('Service Tag', '').strip(),
                            defaults={
                                'make': row.get('Make', '').strip() or None,
                                'description': row.get('Description', '').strip() or None,
                                'status': row.get('Status', 'active').strip() or 'active',
                                'location': row.get('Location', '').strip() or None,
                                'notes': row.get('Notes', '').strip() or None,
                            }
                        )
                    elif asset_type == 'monitors':
                        monitors.objects.update_or_create(
                            asset_tag=row.get('Asset Tag', '').strip(),
                            defaults={
                                'service_tag': row.get('Service Tag', '').strip() or None,
                                'make': row.get('Make', '').strip() or None,
                                'status': row.get('Status', 'active').strip() or 'active',
                                'location': row.get('Location', '').strip() or None,
                                'notes': row.get('Notes', '').strip() or None,
                            }
                        )
                    elif asset_type == 'docking_stations':
                        docking_stations.objects.update_or_create(
                            asset_tag=row.get('Asset Tag', '').strip(),
                            defaults={
                                'service_tag': row.get('Service Tag', '').strip() or None,
                                'make': row.get('Make', '').strip() or None,
                                'status': row.get('Status', 'active').strip() or 'active',
                                'location': row.get('Location', '').strip() or None,
                                'notes': row.get('Notes', '').strip() or None,
                            }
                        )

                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {row_num}: {str(e)}")

            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} records.')
            if error_count > 0:
                messages.warning(request, f'{error_count} records failed. Errors: {"; ".join(errors[:5])}')

        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')

        return redirect('bulk_import')

    return render(request, 'bulk_import.html')


# ==================== QR Code Generation ====================

@user_passes_test(is_admin, login_url='/admin/login/')
def generate_qr_code(request, asset_type, asset_id):
    """Generate QR code for an asset"""
    try:
        import qrcode
        from io import BytesIO

        # Build the URL for the asset
        base_url = request.build_absolute_uri('/')[:-1]

        if asset_type == 'computer':
            url = f"{base_url}/computer/{asset_id}/"
            asset = get_object_or_404(Computers, id=asset_id)
            label = f"Computer: {asset.asset_tag or asset_id}"
        elif asset_type == 'printer':
            url = f"{base_url}/printer/{asset_id}/"
            asset = get_object_or_404(printers, id=asset_id)
            label = f"Printer: {asset.service_tag or asset_id}"
        elif asset_type == 'monitor':
            url = f"{base_url}/monitor/{asset_id}/"
            asset = get_object_or_404(monitors, id=asset_id)
            label = f"Monitor: {asset.asset_tag or asset_id}"
        elif asset_type == 'docking_station':
            url = f"{base_url}/dockingstation/{asset_id}/"
            asset = get_object_or_404(docking_stations, id=asset_id)
            label = f"Docking Station: {asset.asset_tag or asset_id}"
        else:
            return JsonResponse({'error': 'Invalid asset type'}, status=400)

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Return as image response
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="{asset_type}_{asset_id}_qr.png"'
        return response

    except ImportError:
        return JsonResponse({
            'error': 'QR code generation requires the qrcode library. Install with: pip install qrcode[pil]'
        }, status=500)


# ==================== Asset History View ====================

@user_passes_test(is_admin, login_url='/admin/login/')
def asset_history(request, asset_type=None, asset_id=None):
    """View asset change history"""
    history = AssetHistory.objects.select_related('changed_by').order_by('-changed_at')

    if asset_type:
        history = history.filter(asset_type__iexact=asset_type)
    if asset_id:
        history = history.filter(asset_id=asset_id)

    # Apply filters
    action_filter = request.GET.get('action', '')
    if action_filter:
        history = history.filter(action=action_filter)

    date_from = request.GET.get('date_from', '')
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            history = history.filter(changed_at__date__gte=date_from_obj)
        except ValueError:
            pass

    date_to = request.GET.get('date_to', '')
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            history = history.filter(changed_at__date__lte=date_to_obj)
        except ValueError:
            pass

    # Paginate
    history = paginate_queryset(request, history, per_page=50)

    context = {
        'history': history,
        'asset_type': asset_type,
        'asset_id': asset_id,
        'action_filter': action_filter,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, 'asset_history.html', context)


# ==================== Asset Assignment Views ====================

@user_passes_test(is_admin, login_url='/admin/login/')
def assignment_list(request):
    """List all asset assignments"""
    assignments = AssetAssignment.objects.select_related(
        'assigned_by', 'approved_by'
    ).order_by('-assigned_date')

    status_filter = request.GET.get('status', '')
    if status_filter:
        assignments = assignments.filter(status=status_filter)

    assignments = paginate_queryset(request, assignments, per_page=25)

    context = {
        'assignments': assignments,
        'status_choices': AssetAssignment.STATUS_CHOICES,
        'status_filter': status_filter,
    }

    return render(request, 'assignment_list.html', context)


@user_passes_test(is_admin, login_url='/admin/login/')
def create_assignment(request):
    """Create new asset assignment"""
    if request.method == 'POST':
        asset_type = request.POST.get('asset_type')
        asset_id = request.POST.get('asset_id')
        assigned_to = request.POST.get('assigned_to')
        notes = request.POST.get('notes', '')

        assignment = AssetAssignment.objects.create(
            asset_type=asset_type,
            asset_id=asset_id,
            assigned_to=assigned_to,
            assigned_by=request.user,
            notes=notes,
            status='pending'
        )

        messages.success(request, f'Assignment created for {asset_type} {asset_id}.')
        return redirect('assignment_list')

    # Get available assets for dropdowns
    computers = Computers.objects.filter(status='active').values('id', 'asset_tag')
    printer_list = printers.objects.filter(status='active').values('id', 'service_tag')
    monitor_list = monitors.objects.filter(status='active').values('id', 'asset_tag')
    docking_list = docking_stations.objects.filter(status='active').values('id', 'asset_tag')

    context = {
        'computers': list(computers),
        'printers': list(printer_list),
        'monitors': list(monitor_list),
        'docking_stations': list(docking_list),
    }

    return render(request, 'create_assignment.html', context)


@user_passes_test(is_admin, login_url='/admin/login/')
def approve_assignment(request, assignment_id):
    """Approve an assignment"""
    assignment = get_object_or_404(AssetAssignment, id=assignment_id)

    if assignment.status != 'pending':
        messages.error(request, 'This assignment cannot be approved.')
        return redirect('assignment_list')

    assignment.status = 'approved'
    assignment.approved_by = request.user
    assignment.save()

    messages.success(request, 'Assignment approved.')
    return redirect('assignment_list')


@user_passes_test(is_admin, login_url='/admin/login/')
def reject_assignment(request, assignment_id):
    """Reject an assignment"""
    assignment = get_object_or_404(AssetAssignment, id=assignment_id)

    if assignment.status != 'pending':
        messages.error(request, 'This assignment cannot be rejected.')
        return redirect('assignment_list')

    assignment.status = 'rejected'
    assignment.approved_by = request.user
    assignment.save()

    messages.success(request, 'Assignment rejected.')
    return redirect('assignment_list')


@user_passes_test(is_admin, login_url='/admin/login/')
def checkout_assignment(request, assignment_id):
    """Mark assignment as checked out"""
    assignment = get_object_or_404(AssetAssignment, id=assignment_id)

    if assignment.status != 'approved':
        messages.error(request, 'Only approved assignments can be checked out.')
        return redirect('assignment_list')

    assignment.status = 'checked_out'
    assignment.save()

    messages.success(request, 'Asset checked out.')
    return redirect('assignment_list')


@user_passes_test(is_admin, login_url='/admin/login/')
def return_assignment(request, assignment_id):
    """Mark assignment as returned"""
    assignment = get_object_or_404(AssetAssignment, id=assignment_id)

    if assignment.status != 'checked_out':
        messages.error(request, 'Only checked out assignments can be returned.')
        return redirect('assignment_list')

    assignment.status = 'returned'
    assignment.returned_date = timezone.now()
    assignment.save()

    messages.success(request, 'Asset returned.')
    return redirect('assignment_list')
