from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Computers,printers,docking_stations,monitors
from .forms import computersForm,printersForm,docking_stationsForm,monitorsForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.admin.views.decorators import user_passes_test

from django.db.models.signals import pre_save
from django.dispatch import receiver


# Define a function that checks if the user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff and user.is_superuser

@user_passes_test(is_admin, login_url='/admin/login/')
def home(request):
    computer_items = Computers.objects.all()
    return render(request, 'home.html',{'computer_items': computer_items})

#--------------------------computers----------------------------------------
@user_passes_test(is_admin, login_url='/admin/login/')
def index(request):
    return render(request, 'index.html')

@user_passes_test(is_admin, login_url='/admin/login/')
def save_barcode(request):
    print("Request received:", request)
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
    computer = Computers.objects.get(asset_tag=barcode)
    url = reverse('computer_form', kwargs={'barcode': barcode})
    if request.method == 'POST':
        form = computersForm(request.POST, instance=computer)
        if form.is_valid():
            form.save()
            return redirect('computer_list')
        else:
           print(form.errors)
        
        
    else:
        form = computersForm(instance=computer)

   
    return render(request, 'computer_form.html', {'form': form, 'url': url,"pc": computer})

def computers_form(request, pk):
    computer = Computers.objects.get(id=pk)
    form =computersForm(instance=computer)
    if request.method == 'POST':
        form = computersForm(request.POST,instance=computer)
        if form.is_valid():
            form.save()
            messages.success(
                request, "computer's data has been updated.")
            return redirect('computer_list')
            

  
    context = {"form":form,"pc": computer}

    return render(request, "computer_form.html", context)

@user_passes_test(is_admin, login_url='/admin/login/')
def delete_computer(request, pk):
    computer = Computers.objects.get(id=pk)
    computer.delete()
    messages.success(request, "computer's data has been deleted.")
    return redirect('computer_list')



@user_passes_test(is_admin, login_url='/admin/login/')

def computer_list(request):
    computer_items = Computers.objects.all()
    return render(request, 'computer_list.html', {'computer_items': computer_items})

#----------------------printers view----------------------------
@user_passes_test(is_admin, login_url='/admin/login/')

def update_printer_view(request, pk):
    printer = printers.objects.get(id=pk)
    printerform = printersForm(instance=printer)
    mydict = {'form':printerform,"printers":printer}
    if request.method == 'POST':
        Printerform = printersForm(request.POST, instance=printer)
        if Printerform.is_valid():
            Printer= Printerform.save()
            Printer.save()
            messages.success(
                request, 'printer data has been updated.')
        
            return redirect('printers_list')
        else:
            messages.error(request, 'error while updateing printer data.')
            
            return redirect('printers_list')
    return render(request, 'printersform.html', context=mydict)

@user_passes_test(is_admin, login_url='/admin/login/')
def delete_printer(request, pk):
    printer = printers.objects.get(id=pk)
    printer.delete()
    messages.success(request, "printer has been deleted.")
    return redirect('printers_list')

@user_passes_test(is_admin, login_url='/admin/login/')
def add_printer(request):
    if request.method == 'POST':
        printerform = printersForm(request.POST)
        if printerform.is_valid():
            printerform.save()
            messages.success(
                request, 'printer data has been added.')
            return redirect('home')
        else:
            messages.error(
                request, 'error while adding printer')
            print('printer form error')
            return redirect('add_printer')
    else:
        printerform = printersForm()

    return render(request, 'add_printer.html',{"form":printerform})


@user_passes_test(is_admin, login_url='/admin/login/')

def printer_list(request):
    printer_items = printers.objects.all()
    return render(request, 'printer_list.html', {'printer_items': printer_items})
#------------------monitor veiws----------------------------

@user_passes_test(is_admin, login_url='/admin/login/')

def update_monitor_view(request, pk):
    monitor = monitors.objects.get(id=pk)
    monitorform = monitorsForm(instance=monitor)
    mydict = {'form':monitorform,"monitor":monitor}
    if request.method == 'POST':
        Monitorform = monitorsForm(request.POST, instance=monitor)
        if Monitorform.is_valid():
            Monitor= Monitorform.save()
            Monitor.save()
            messages.success(
                request, 'Monitor data has been updated.')
        
           
        else:
            messages.error(
                request, 'erro')
            print('Monitor form error')
           
    return render(request, 'monitors_form.html', context=mydict)

@user_passes_test(is_admin, login_url='/admin/login/')
def scan_mointor(request):
    return render(request, 'scan_monitor.html')


@user_passes_test(is_admin, login_url='/admin/login/')
def save_barcode_monitor(request):
    print("Request received:", request)
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
    monitor = monitors.objects.get(asset_tag=barcode)
    url = reverse('monitor_form', kwargs={'barcode': barcode})
    if request.method == 'POST':
        form = monitorsForm(request.POST, instance=monitor)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
           print(form.errors)
        
        
    else:
        form = monitorsForm(instance=monitor)
    return render(request, 'monitors_form.html', {'form': form, 'url': url,"monitor":monitor})

@user_passes_test(is_admin, login_url='/admin/login/')
def delete_monitor(request, pk):
    monitor = monitors.objects.get(id=pk)
    monitor.delete()
    messages.success(request, "monitor has been deleted.")
    return redirect('monitors_list')

   
    return render(request, 'monitors_form.html', {'form': form, 'url': url})
@user_passes_test(is_admin, login_url='/admin/login/')
def monitor_list(request):
    monitor_items = monitors.objects.all()
    return render(request, 'monitor_list.html', {'monitor_items': monitor_items})
#------------------------------docking station views----------------------------------
@user_passes_test(is_admin, login_url='/admin/login/')

def update_dockingstation_view(request, pk):
    dockingstation = docking_stations.objects.get(id=pk)
    dockistationform = docking_stationsForm(instance=dockingstation)
    mydict = {'form':dockistationform,'dockingstation':dockingstation}
    if request.method == 'POST':
        Dockingstaionform = docking_stationsForm(request.POST, instance=dockingstation)
        if Dockingstaionform.is_valid():
            Dockingstaion= Dockingstaionform.save()
            Dockingstaion.save()
            messages.success(
                request, 'Docking staion data has been updated.')
        
            return redirect('home')
        else:
            messages.error(
                request, 'error')
            print('Dockingstaion form error')
            return redirect('home')
    return render(request, 'docking_stations_form.html', context=mydict)

@user_passes_test(is_admin, login_url='/admin/login/')
def delete_dockingstation(request, pk):
    dockingstation = docking_stations.objects.get(id=pk)
    dockingstation.delete()
    messages.success(request, "docking station has been deleted.")
    return redirect('dockingstation_list')

@user_passes_test(is_admin, login_url='/admin/login/')
def scan_dockingstation(request):
    return render(request, 'scan_docking_station.html')


@user_passes_test(is_admin, login_url='/admin/login/')
def save_barcode_dockingstation(request):
    print("Request received:", request)
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
def dockingtation_form(request, barcode):
    dockingstaion = docking_stations.objects.get(asset_tag=barcode)
    url = reverse('dockingstation_form', kwargs={'barcode': barcode})
    if request.method == 'POST':
        form = docking_stationsForm(request.POST, instance=dockingstaion)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
           print(form.errors)
        
        
    else:
        form = monitorsForm(instance=dockingstaion)

   
    return render(request, 'docking_stations_form.html', {'form': form, 'url': url,'dockingstation':dockingstation})
@user_passes_test(is_admin, login_url='/admin/login/')

def dockingstation_list(request):
    dockingstation_items = docking_stations.objects.all()
    return render(request, 'docking_station_list.html', {'dockingstation_items': dockingstation_items})
