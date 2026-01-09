from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Max
from .models import printers, Computers, docking_stations, monitors


def get_next_id(model_class, prefix):
    """
    Generate the next ID for a model using numeric extraction.
    This properly handles numeric ordering (e.g., computer-9 comes before computer-10).
    """
    # Get all existing IDs and extract the numeric part
    existing_ids = model_class.objects.values_list('id', flat=True)
    max_num = 0
    for existing_id in existing_ids:
        try:
            parts = existing_id.split('-')
            if len(parts) >= 2:
                num = int(parts[-1])
                if num > max_num:
                    max_num = num
        except (ValueError, IndexError):
            continue
    return f"{prefix}-{max_num + 1}"


@receiver(pre_save, sender=Computers)
def generate_computer_id(sender, instance, **kwargs):
    if not instance.id:
        instance.id = get_next_id(Computers, "computer")


@receiver(pre_save, sender=printers)
def generate_printer_id(sender, instance, **kwargs):
    if not instance.id:
        instance.id = get_next_id(printers, "printer")


@receiver(pre_save, sender=monitors)
def generate_monitor_id(sender, instance, **kwargs):
    if not instance.id:
        instance.id = get_next_id(monitors, "monitor")


@receiver(pre_save, sender=docking_stations)
def generate_docking_station_id(sender, instance, **kwargs):
    if not instance.id:
        instance.id = get_next_id(docking_stations, "docking_station")

