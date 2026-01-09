from django import forms
from .models import (
    Computers, docking_stations, printers, monitors,
    AssetStatus, AssetAssignment, NotificationSetting
)


class computersForm(forms.ModelForm):
    """Form for creating/editing computers"""
    class Meta:
        model = Computers
        fields = [
            "asset_tag", "service_tag", "computer_name", 'department',
            'user', 'make', 'model', 'storage', 'cpu', 'ram', 'printers',
            'status', 'location', 'purchase_date', 'warranty_expiry',
            'purchase_cost', 'notes'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'purchase_cost': forms.NumberInput(attrs={'step': '0.01'}),
        }


class printersForm(forms.ModelForm):
    """Form for creating/editing printers"""
    class Meta:
        model = printers
        fields = [
            'service_tag', 'make', 'description',
            'status', 'location', 'purchase_date', 'warranty_expiry',
            'purchase_cost', 'notes'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'purchase_cost': forms.NumberInput(attrs={'step': '0.01'}),
        }


class monitorsForm(forms.ModelForm):
    """Form for creating/editing monitors"""
    class Meta:
        model = monitors
        fields = [
            'asset_tag', 'service_tag', 'make', 'computer',
            'status', 'location', 'purchase_date', 'warranty_expiry',
            'purchase_cost', 'notes'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'purchase_cost': forms.NumberInput(attrs={'step': '0.01'}),
        }


class docking_stationsForm(forms.ModelForm):
    """Form for creating/editing docking stations"""
    class Meta:
        model = docking_stations
        fields = [
            'asset_tag', 'service_tag', 'make', 'computer',
            'status', 'location', 'purchase_date', 'warranty_expiry',
            'purchase_cost', 'notes'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'purchase_cost': forms.NumberInput(attrs={'step': '0.01'}),
        }


class AssetAssignmentForm(forms.ModelForm):
    """Form for creating asset assignments"""
    class Meta:
        model = AssetAssignment
        fields = ['asset_type', 'asset_id', 'assigned_to', 'due_date', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class NotificationSettingForm(forms.ModelForm):
    """Form for user notification settings"""
    class Meta:
        model = NotificationSetting
        fields = [
            'warranty_reminder_days', 'email_on_assignment',
            'email_on_warranty_expiry', 'daily_summary', 'weekly_summary'
        ]


class BulkImportForm(forms.Form):
    """Form for bulk CSV import"""
    ASSET_TYPE_CHOICES = [
        ('computers', 'Computers'),
        ('printers', 'Printers'),
        ('monitors', 'Monitors'),
        ('docking_stations', 'Docking Stations'),
    ]

    asset_type = forms.ChoiceField(choices=ASSET_TYPE_CHOICES)
    csv_file = forms.FileField(
        help_text='Upload a CSV file with asset data. Download a template first.'
    )


class SearchForm(forms.Form):
    """Form for advanced search"""
    q = forms.CharField(required=False, label='Search')
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(AssetStatus.choices),
        required=False
    )
    department = forms.CharField(required=False)
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
