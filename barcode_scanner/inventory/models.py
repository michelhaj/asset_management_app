from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AssetStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    RETIRED = 'retired', 'Retired'
    IN_REPAIR = 'repair', 'In Repair'
    DISPOSED = 'disposed', 'Disposed'
    AVAILABLE = 'available', 'Available'


class BaseAsset(models.Model):
    """Abstract base model for common asset fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AssetStatus.choices,
        default=AssetStatus.ACTIVE
    )
    location = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class Computers(BaseAsset):
    id = models.CharField(primary_key=True, max_length=255, blank=True, null=False)
    asset_tag = models.CharField(max_length=255, blank=True, null=True, unique=True)
    service_tag = models.CharField(max_length=255, blank=True, null=True, unique=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    computer_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.CharField(max_length=255, blank=True, null=True)
    make = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    storage = models.CharField(max_length=255, blank=True, null=True)
    cpu = models.CharField(max_length=255, blank=True, null=True)
    ram = models.CharField(max_length=255, blank=True, null=True)
    printers = models.ManyToManyField('printers', related_name='Computers', blank=True)

    def __str__(self):
        return f"{self.make} - {self.asset_tag} - {self.id}"

    class Meta:
        verbose_name = "Computer"
        verbose_name_plural = "Computers"
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['user']),
            models.Index(fields=['make', 'model']),
            models.Index(fields=['status']),
            models.Index(fields=['asset_tag']),
            models.Index(fields=['service_tag']),
        ]
        permissions = [
            ("can_view_computers", "Can view computers"),
            ("can_edit_computers", "Can edit computers"),
            ("can_delete_computers", "Can delete computers"),
            ("can_export_computers", "Can export computers"),
        ]


class printers(BaseAsset):
    id = models.CharField(primary_key=True, max_length=255, blank=True, null=False)
    service_tag = models.CharField(max_length=255, unique=True)
    make = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.service_tag} - {self.description} - {self.id}"

    class Meta:
        verbose_name = "Printer"
        verbose_name_plural = "Printers"
        indexes = [
            models.Index(fields=['service_tag']),
            models.Index(fields=['status']),
        ]
        permissions = [
            ("can_view_printers", "Can view printers"),
            ("can_edit_printers", "Can edit printers"),
            ("can_delete_printers", "Can delete printers"),
            ("can_export_printers", "Can export printers"),
        ]


class docking_stations(BaseAsset):
    id = models.CharField(primary_key=True, max_length=255, blank=True, null=False)
    asset_tag = models.CharField(max_length=255, blank=True, null=True, unique=True)
    service_tag = models.CharField(max_length=255, blank=True, null=True)
    make = models.CharField(max_length=255, blank=True, null=True)
    computer = models.ForeignKey(
        Computers, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='docking_stations'
    )

    def __str__(self):
        return f"{self.asset_tag} - {self.make} - {self.id}"

    class Meta:
        verbose_name = "Docking Station"
        verbose_name_plural = "Docking Stations"
        indexes = [
            models.Index(fields=['asset_tag']),
            models.Index(fields=['status']),
        ]
        permissions = [
            ("can_view_docking_stations", "Can view docking stations"),
            ("can_edit_docking_stations", "Can edit docking stations"),
            ("can_delete_docking_stations", "Can delete docking stations"),
            ("can_export_docking_stations", "Can export docking stations"),
        ]


class monitors(BaseAsset):
    id = models.CharField(primary_key=True, max_length=255, blank=True, null=False)
    asset_tag = models.CharField(max_length=255, blank=True, null=True, unique=True)
    service_tag = models.CharField(max_length=255, blank=True, null=True, unique=True)
    make = models.CharField(max_length=255, blank=True, null=True)
    computer = models.ForeignKey(
        Computers, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='monitors'
    )

    def __str__(self):
        return f"{self.asset_tag} - {self.make} - {self.id}"

    class Meta:
        verbose_name = "Monitor"
        verbose_name_plural = "Monitors"
        indexes = [
            models.Index(fields=['asset_tag']),
            models.Index(fields=['service_tag']),
            models.Index(fields=['status']),
        ]
        permissions = [
            ("can_view_monitors", "Can view monitors"),
            ("can_edit_monitors", "Can edit monitors"),
            ("can_delete_monitors", "Can delete monitors"),
            ("can_export_monitors", "Can export monitors"),
        ]


class AssetHistory(models.Model):
    """Audit trail model to track all asset changes"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('assigned', 'Assigned'),
        ('unassigned', 'Unassigned'),
    ]

    asset_type = models.CharField(max_length=50)
    asset_id = models.CharField(max_length=255)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Asset History"
        verbose_name_plural = "Asset Histories"
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['asset_type', 'asset_id']),
            models.Index(fields=['changed_at']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.asset_type} {self.asset_id} - {self.action} at {self.changed_at}"


class AssetAssignment(models.Model):
    """Track asset assignments to users with workflow"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('checked_out', 'Checked Out'),
        ('returned', 'Returned'),
    ]

    asset_type = models.CharField(max_length=50)
    asset_id = models.CharField(max_length=255)
    assigned_to = models.CharField(max_length=255)  # Employee name/ID
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='assignments_made'
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assignments_approved'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    returned_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    digital_signature = models.TextField(blank=True, null=True)  # Base64 encoded signature

    class Meta:
        verbose_name = "Asset Assignment"
        verbose_name_plural = "Asset Assignments"
        ordering = ['-assigned_date']
        indexes = [
            models.Index(fields=['asset_type', 'asset_id']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.asset_type} {self.asset_id} -> {self.assigned_to}"


class NotificationSetting(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    warranty_reminder_days = models.IntegerField(default=30)
    email_on_assignment = models.BooleanField(default=True)
    email_on_warranty_expiry = models.BooleanField(default=True)
    daily_summary = models.BooleanField(default=False)
    weekly_summary = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification settings for {self.user.username}"
