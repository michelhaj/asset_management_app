from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import (
    printers, Computers, docking_stations, monitors,
    AssetHistory
)

# Thread-local storage for request context
import threading
_thread_locals = threading.local()


def set_current_user(user):
    """Set current user in thread-local storage"""
    _thread_locals.user = user


def get_current_user():
    """Get current user from thread-local storage"""
    return getattr(_thread_locals, 'user', None)


def set_current_ip(ip):
    """Set current IP in thread-local storage"""
    _thread_locals.ip = ip


def get_current_ip():
    """Get current IP from thread-local storage"""
    return getattr(_thread_locals, 'ip', None)


# ==================== ID Generation Signals ====================

def get_max_id_number(model, prefix):
    """
    Extract the maximum numeric ID from a model's records.
    Handles IDs like 'prefix-1', 'prefix-10', etc. correctly using numeric comparison.
    """
    max_num = 0
    for item in model.objects.filter(id__startswith=f"{prefix}-").values_list('id', flat=True):
        try:
            num = int(item.split('-')[1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            continue
    return max_num


@receiver(pre_save, sender=Computers)
def generate_computer_id(sender, instance, **kwargs):
    if not instance.id:
        max_num = get_max_id_number(Computers, "computer")
        instance.id = f"computer-{max_num + 1}"


@receiver(pre_save, sender=printers)
def generate_printer_id(sender, instance, **kwargs):
    if not instance.id:
        max_num = get_max_id_number(printers, "printer")
        instance.id = f"printer-{max_num + 1}"


@receiver(pre_save, sender=monitors)
def generate_monitor_id(sender, instance, **kwargs):
    if not instance.id:
        max_num = get_max_id_number(monitors, "monitor")
        instance.id = f"monitor-{max_num + 1}"


@receiver(pre_save, sender=docking_stations)
def generate_docking_station_id(sender, instance, **kwargs):
    if not instance.id:
        max_num = get_max_id_number(docking_stations, "docking_station")
        instance.id = f"docking_station-{max_num + 1}"


# ==================== Audit Trail Signals ====================

def get_model_fields(instance):
    """Get serializable fields from model instance"""
    data = {}
    for field in instance._meta.fields:
        value = getattr(instance, field.name)
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        elif hasattr(value, 'pk'):
            value = str(value.pk)
        else:
            value = str(value) if value is not None else None
        data[field.name] = value
    return data


def create_audit_log(asset_type, asset_id, action, old_values=None, new_values=None):
    """Create an audit log entry"""
    AssetHistory.objects.create(
        asset_type=asset_type,
        asset_id=asset_id,
        action=action,
        changed_by=get_current_user(),
        old_values=old_values,
        new_values=new_values,
        ip_address=get_current_ip()
    )


# Store original values before save
@receiver(pre_save, sender=Computers)
def store_computer_original(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._original = Computers.objects.get(pk=instance.pk)
        except Computers.DoesNotExist:
            instance._original = None
    else:
        instance._original = None


@receiver(pre_save, sender=printers)
def store_printer_original(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._original = printers.objects.get(pk=instance.pk)
        except printers.DoesNotExist:
            instance._original = None
    else:
        instance._original = None


@receiver(pre_save, sender=monitors)
def store_monitor_original(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._original = monitors.objects.get(pk=instance.pk)
        except monitors.DoesNotExist:
            instance._original = None
    else:
        instance._original = None


@receiver(pre_save, sender=docking_stations)
def store_docking_station_original(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._original = docking_stations.objects.get(pk=instance.pk)
        except docking_stations.DoesNotExist:
            instance._original = None
    else:
        instance._original = None


# Create audit logs after save
@receiver(post_save, sender=Computers)
def audit_computer_save(sender, instance, created, **kwargs):
    if created:
        create_audit_log(
            asset_type='Computer',
            asset_id=instance.id,
            action='created',
            new_values=get_model_fields(instance)
        )
    else:
        old_values = get_model_fields(instance._original) if hasattr(instance, '_original') and instance._original else None
        new_values = get_model_fields(instance)
        if old_values != new_values:
            create_audit_log(
                asset_type='Computer',
                asset_id=instance.id,
                action='updated',
                old_values=old_values,
                new_values=new_values
            )


@receiver(post_save, sender=printers)
def audit_printer_save(sender, instance, created, **kwargs):
    if created:
        create_audit_log(
            asset_type='Printer',
            asset_id=instance.id,
            action='created',
            new_values=get_model_fields(instance)
        )
    else:
        old_values = get_model_fields(instance._original) if hasattr(instance, '_original') and instance._original else None
        new_values = get_model_fields(instance)
        if old_values != new_values:
            create_audit_log(
                asset_type='Printer',
                asset_id=instance.id,
                action='updated',
                old_values=old_values,
                new_values=new_values
            )


@receiver(post_save, sender=monitors)
def audit_monitor_save(sender, instance, created, **kwargs):
    if created:
        create_audit_log(
            asset_type='Monitor',
            asset_id=instance.id,
            action='created',
            new_values=get_model_fields(instance)
        )
    else:
        old_values = get_model_fields(instance._original) if hasattr(instance, '_original') and instance._original else None
        new_values = get_model_fields(instance)
        if old_values != new_values:
            create_audit_log(
                asset_type='Monitor',
                asset_id=instance.id,
                action='updated',
                old_values=old_values,
                new_values=new_values
            )


@receiver(post_save, sender=docking_stations)
def audit_docking_station_save(sender, instance, created, **kwargs):
    if created:
        create_audit_log(
            asset_type='Docking Station',
            asset_id=instance.id,
            action='created',
            new_values=get_model_fields(instance)
        )
    else:
        old_values = get_model_fields(instance._original) if hasattr(instance, '_original') and instance._original else None
        new_values = get_model_fields(instance)
        if old_values != new_values:
            create_audit_log(
                asset_type='Docking Station',
                asset_id=instance.id,
                action='updated',
                old_values=old_values,
                new_values=new_values
            )


# Audit logs for delete
@receiver(post_delete, sender=Computers)
def audit_computer_delete(sender, instance, **kwargs):
    create_audit_log(
        asset_type='Computer',
        asset_id=instance.id,
        action='deleted',
        old_values=get_model_fields(instance)
    )


@receiver(post_delete, sender=printers)
def audit_printer_delete(sender, instance, **kwargs):
    create_audit_log(
        asset_type='Printer',
        asset_id=instance.id,
        action='deleted',
        old_values=get_model_fields(instance)
    )


@receiver(post_delete, sender=monitors)
def audit_monitor_delete(sender, instance, **kwargs):
    create_audit_log(
        asset_type='Monitor',
        asset_id=instance.id,
        action='deleted',
        old_values=get_model_fields(instance)
    )


@receiver(post_delete, sender=docking_stations)
def audit_docking_station_delete(sender, instance, **kwargs):
    create_audit_log(
        asset_type='Docking Station',
        asset_id=instance.id,
        action='deleted',
        old_values=get_model_fields(instance)
    )
