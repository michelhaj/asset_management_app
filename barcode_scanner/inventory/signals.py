from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import printers,Computers,docking_stations,monitors

@receiver(pre_save, sender=Computers)
def generate_printer_id(sender, instance, **kwargs):
    if not instance.id:
        last_id = Computers.objects.order_by('-id').first()
        if last_id:
            instance.id = f"computer-{int(last_id.id.split('-')[1]) + 1}"
        else:
            instance.id = "computer-1"

@receiver(pre_save, sender=printers)
def generate_printer_id(sender, instance, **kwargs):
    if not instance.id:
        last_id = printers.objects.order_by('-id').first()
        if last_id:
            instance.id = f"printer-{int(last_id.id.split('-')[1]) + 1}"
        else:
            instance.id = "printer-1"

@receiver(pre_save, sender=monitors)
def generate_printer_id(sender, instance, **kwargs):
    if not instance.id:
        last_id = monitors.objects.order_by('-id').first()
        if last_id:
            instance.id = f"monitor-{int(last_id.id.split('-')[1]) + 1}"
        else:
            instance.id = "monitor-1"

@receiver(pre_save, sender=docking_stations)
def generate_printer_id(sender, instance, **kwargs):
    if not instance.id:
        last_id = docking_stations.objects.order_by('-id').first()
        if last_id:
            instance.id = f"docking_station-{int(last_id.id.split('-')[1]) + 1}"
        else:
            instance.id = "docking_station-1"

