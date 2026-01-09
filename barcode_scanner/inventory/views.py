import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Computers, printers, docking_stations, monitors
from .forms import computersForm, printersForm, docking_stationsForm, monitorsForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.admin.views.decorators import user_passes_test

logger = logging.getLogger(__name__)


# Define a function that checks if the user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff and user.is_superuser

@user_passes_test(is_admin, login_url='/admin/login/')
def home(request):
    # Use prefetch_related to avoid N+1 query problem
    computer_items = Computers.objects.prefetch_related(
        'printers', 'docking_stations', 'monitors'
    ).all()
    return render(request, 'home.html', {'computer_items': computer_items})

#--------------------------computers----------------------------------------
@user_passes_test(is_admin, login_url='/admin/login/')
def index(request):
    return render(request, 'index.html')

@user_passes_test(is_admin, login_url='/admin/login/')
def save_barcode(request):
    logger.debug("Save barcode request received")
    if request.method == 'POST':
        barcode_data = request.POST.get('barcode_data', None)
        if barcode_data:
            computer, created = Computers.objects.get_or_create(asset_tag=barcode_data)
            if created:
                return JsonResponse({'status': 'success', 'message': 'Barcode saved successfully', 'new_item': True})
            else:
                return JsonResponse({'status': 'success', 'message': 'Barcode already exists', 'existing_item': True})
        else:
            return JsonResponse({'status': 'error', 'message': 'No barcode data received'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@user_passes_test(is_admin, login_url='/admin/login/')
def computer_form(request, barcode):
    computer = get_object_or_404(Computers, asset_tag=barcode)
    url = reverse('computer_form', kwargs={'barcode': barcode})
    if request.method == 'POST':
        form = computersForm(request.POST, instance=computer)
        if form.is_valid():
            form.save()
            return redirect('computer_list')
        else:
            logger.warning("Computer form errors: %s", form.errors)
    else:
        form = computersForm(instance=computer)

    return render(request, 'computer_form.html', {'form': form, 'url': url, "pc": computer})

@user_passes_test(is_admin, login_url='/admin/login/')
def computers_form(request, pk):
    computer = get_object_or_404(Computers, id=pk)
    form = computersForm(instance=computer)
    if request.method == 'POST':
        form = computersForm(request.POST, instance=computer)
        if form.is_valid():
            form.save()
            messages.success(request, "Computer's data has been updated.")
            return redirect('computer_list')

    context = {"form": form, "pc": computer}
    return render(request, "computer_form.html", context)

@user_passes_test(is_admin, login_url='/admin/login/')
def delete_computer(request, id):
    computer = get_object_or_404(Computers, id=id)
    computer.delete()
    messages.success(request, "Computer's data has been deleted.")
    logger.info("Computer deleted: %s", id)
    return redirect('computer_list')
@user_passes_test(is_admin, login_url='/admin/login/')
def add_computer(request):
    if request.method == 'POST':
        computerform = computersForm(request.POST)
        if computerform.is_valid():
            computerform.save()
            messages.success(request, 'Computer data has been added.')
            return redirect('home')
        else:
            messages.error(request, 'Error while adding computer data.')
            return redirect('add_computer')
    else:
        computerform = computersForm()

    return render(request, 'computer_form.html', {"form": computerform})

@user_passes_test(is_admin, login_url='/admin/login/')
def computer_list(request):
    computer_items = Computers.objects.all()
    return render(request, 'computer_list.html', {'computer_items': computer_items})


@user_passes_test(is_admin, login_url='/admin/login/')
def update_printer_view(request, pk):
    printer = get_object_or_404(printers, id=pk)
    printerform = printersForm(instance=printer)
    mydict = {'form': printerform, "printers": printer}
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
    printer = get_object_or_404(printers, id=id)
    printer.delete()
    messages.success(request, "Printer has been deleted.")
    logger.info("Printer deleted: %s", id)
    return redirect('printers_list')


@user_passes_test(is_admin, login_url='/admin/login/')
def add_printer(request):
    if request.method == 'POST':
        printerform = printersForm(request.POST)
        if printerform.is_valid():
            printerform.save()
            messages.success(request, 'Printer data has been added.')
            return redirect('home')
        else:
            messages.error(request, 'Error while adding printer.')
            logger.warning("Printer form error: %s", printerform.errors)
            return redirect('add_printer')
    else:
        printerform = printersForm()

    return render(request, 'add_printer.html', {"form": printerform})


@user_passes_test(is_admin, login_url='/admin/login/')
def printer_list(request):
    printer_items = printers.objects.all()
    return render(request, 'printer_list.html', {'printer_items': printer_items})
@user_passes_test(is_admin, login_url='/admin/login/')
def update_monitor_view(request, pk):
    monitor = get_object_or_404(monitors, id=pk)
    monitorform = monitorsForm(instance=monitor)
    mydict = {'form': monitorform, "monitor": monitor}
    if request.method == 'POST':
        monitorform = monitorsForm(request.POST, instance=monitor)
        if monitorform.is_valid():
            monitorform.save()
            messages.success(request, 'Monitor data has been updated.')
            return redirect('monitors_list')
        else:
            messages.error(request, 'Error while updating monitor data.')
            logger.warning("Monitor form error: %s", monitorform.errors)
    return render(request, 'monitors_form.html', context=mydict)


@user_passes_test(is_admin, login_url='/admin/login/')
def scan_monitor(request):
    return render(request, 'scan_monitor.html')


@user_passes_test(is_admin, login_url='/admin/login/')
def save_barcode_monitor(request):
    logger.debug("Save barcode monitor request received")
    if request.method == 'POST':
        barcode_data = request.POST.get('barcode_data', None)
        if barcode_data:
            monitor, created = monitors.objects.get_or_create(asset_tag=barcode_data)
            if created:
                return JsonResponse({'status': 'success', 'message': 'Barcode saved successfully', 'new_item': True})
            else:
                return JsonResponse({'status': 'success', 'message': 'Barcode already exists', 'existing_item': True})
        else:
            return JsonResponse({'status': 'error', 'message': 'No barcode data received'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@user_passes_test(is_admin, login_url='/admin/login/')
def monitor_form(request, barcode):
    monitor = get_object_or_404(monitors, asset_tag=barcode)
    url = reverse('monitor_form', kwargs={'barcode': barcode})
    if request.method == 'POST':
        form = monitorsForm(request.POST, instance=monitor)
        if form.is_valid():
            form.save()
            return redirect('monitors_list')
        else:
            logger.warning("Monitor form errors: %s", form.errors)
    else:
        form = monitorsForm(instance=monitor)
    return render(request, 'monitors_form.html', {'form': form, 'url': url, "monitor": monitor})


@user_passes_test(is_admin, login_url='/admin/login/')
def add_monitor(request):
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

    return render(request, 'monitors_form.html', {"form": monitorform})


@user_passes_test(is_admin, login_url='/admin/login/')
def delete_monitor(request, id):
    monitor = get_object_or_404(monitors, id=id)
    monitor.delete()
    messages.success(request, "Monitor has been deleted.")
    logger.info("Monitor deleted: %s", id)
    return redirect('monitors_list')


@user_passes_test(is_admin, login_url='/admin/login/')
def monitor_list(request):
    monitor_items = monitors.objects.all()
    return render(request, 'monitor_list.html', {'monitor_items': monitor_items})
@user_passes_test(is_admin, login_url='/admin/login/')
def update_dockingstation_view(request, pk):
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
            messages.error(request, 'Error while updating docking station data.')
            logger.warning("Docking station form error: %s", dockingstationform.errors)
    return render(request, 'docking_stations_form.html', context=mydict)


@user_passes_test(is_admin, login_url='/admin/login/')
def delete_dockingstation(request, id):
    dockingstation = get_object_or_404(docking_stations, id=id)
    dockingstation.delete()
    messages.success(request, "Docking station has been deleted.")
    logger.info("Docking station deleted: %s", id)
    return redirect('dockingstation_list')


@user_passes_test(is_admin, login_url='/admin/login/')
def scan_dockingstation(request):
    return render(request, 'scan_docking_station.html')


@user_passes_test(is_admin, login_url='/admin/login/')
def save_barcode_dockingstation(request):
    logger.debug("Save barcode docking station request received")
    if request.method == 'POST':
        barcode_data = request.POST.get('barcode_data', None)
        if barcode_data:
            dockingstation, created = docking_stations.objects.get_or_create(asset_tag=barcode_data)
            if created:
                return JsonResponse({'status': 'success', 'message': 'Barcode saved successfully', 'new_item': True})
            else:
                return JsonResponse({'status': 'success', 'message': 'Barcode already exists', 'existing_item': True})
        else:
            return JsonResponse({'status': 'error', 'message': 'No barcode data received'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@user_passes_test(is_admin, login_url='/admin/login/')
def dockingstation_form(request, barcode):
    dockingstation = get_object_or_404(docking_stations, asset_tag=barcode)
    url = reverse('dockingstation_form', kwargs={'barcode': barcode})
    if request.method == 'POST':
        form = docking_stationsForm(request.POST, instance=dockingstation)
        if form.is_valid():
            form.save()
            return redirect('dockingstation_list')
        else:
            logger.warning("Docking station form errors: %s", form.errors)
    else:
        form = docking_stationsForm(instance=dockingstation)

    return render(request, 'docking_stations_form.html', {'form': form, 'url': url, 'dockingstation': dockingstation})


@user_passes_test(is_admin, login_url='/admin/login/')
def add_dockingstation(request):
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

    return render(request, 'docking_stations_form.html', {"form": dockingstationform})


@user_passes_test(is_admin, login_url='/admin/login/')
def dockingstation_list(request):
    dockingstation_items = docking_stations.objects.all()
    return render(request, 'docking_station_list.html', {'dockingstation_items': dockingstation_items})