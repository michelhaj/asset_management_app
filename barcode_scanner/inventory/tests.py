"""
Comprehensive tests for the Asset Management System
"""
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import (
    Computers, printers, monitors, docking_stations,
    AssetHistory, AssetAssignment, AssetStatus, NotificationSetting
)
from .forms import computersForm, printersForm, monitorsForm, docking_stationsForm


class BaseTestCase(TestCase):
    """Base test case with common setup"""

    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='userpass123'
        )
        self.client = Client()


class ComputerModelTests(BaseTestCase):
    """Tests for the Computer model"""

    def test_computer_creation(self):
        """Test creating a computer"""
        computer = Computers.objects.create(
            asset_tag='COMP-001',
            service_tag='SVC-001',
            computer_name='TEST-PC',
            department='IT',
            user='John Doe',
            make='Dell',
            model='OptiPlex 7090'
        )
        self.assertEqual(computer.asset_tag, 'COMP-001')
        self.assertEqual(computer.status, AssetStatus.ACTIVE)
        self.assertIsNotNone(computer.id)
        self.assertTrue(computer.id.startswith('computer-'))

    def test_computer_auto_id_generation(self):
        """Test automatic ID generation for computers"""
        comp1 = Computers.objects.create(asset_tag='COMP-001')
        comp2 = Computers.objects.create(asset_tag='COMP-002')

        self.assertEqual(comp1.id, 'computer-1')
        self.assertEqual(comp2.id, 'computer-2')

    def test_computer_str_representation(self):
        """Test string representation of computer"""
        computer = Computers.objects.create(
            asset_tag='COMP-001',
            make='Dell'
        )
        self.assertIn('Dell', str(computer))
        self.assertIn('COMP-001', str(computer))

    def test_computer_with_lifecycle_fields(self):
        """Test computer with new lifecycle fields"""
        computer = Computers.objects.create(
            asset_tag='COMP-001',
            purchase_date=date.today(),
            warranty_expiry=date.today() + timedelta(days=365),
            purchase_cost=Decimal('1500.00'),
            location='Building A',
            notes='Test computer'
        )
        self.assertEqual(computer.purchase_cost, Decimal('1500.00'))
        self.assertEqual(computer.location, 'Building A')


class PrinterModelTests(BaseTestCase):
    """Tests for the Printer model"""

    def test_printer_creation(self):
        """Test creating a printer"""
        printer = printers.objects.create(
            service_tag='PRT-001',
            make='HP',
            description='LaserJet Pro'
        )
        self.assertEqual(printer.service_tag, 'PRT-001')
        self.assertTrue(printer.id.startswith('printer-'))


class MonitorModelTests(BaseTestCase):
    """Tests for the Monitor model"""

    def test_monitor_creation(self):
        """Test creating a monitor"""
        monitor = monitors.objects.create(
            asset_tag='MON-001',
            service_tag='SVC-MON-001',
            make='Dell'
        )
        self.assertEqual(monitor.asset_tag, 'MON-001')

    def test_monitor_with_computer_relationship(self):
        """Test monitor linked to computer"""
        computer = Computers.objects.create(asset_tag='COMP-001')
        monitor = monitors.objects.create(
            asset_tag='MON-001',
            computer=computer
        )
        self.assertEqual(monitor.computer, computer)
        self.assertIn(monitor, computer.monitors.all())


class DockingStationModelTests(BaseTestCase):
    """Tests for the Docking Station model"""

    def test_docking_station_creation(self):
        """Test creating a docking station"""
        dock = docking_stations.objects.create(
            asset_tag='DOCK-001',
            make='Dell WD19'
        )
        self.assertEqual(dock.asset_tag, 'DOCK-001')


class AssetHistoryTests(BaseTestCase):
    """Tests for the Asset History (audit trail)"""

    def test_history_created_on_new_computer(self):
        """Test that history is created when a new computer is added"""
        computer = Computers.objects.create(asset_tag='COMP-001')

        history = AssetHistory.objects.filter(
            asset_type='Computer',
            asset_id=computer.id,
            action='created'
        )
        self.assertEqual(history.count(), 1)

    def test_history_created_on_update(self):
        """Test that history is created when a computer is updated"""
        computer = Computers.objects.create(asset_tag='COMP-001')
        computer.department = 'IT'
        computer.save()

        history = AssetHistory.objects.filter(
            asset_type='Computer',
            asset_id=computer.id,
            action='updated'
        )
        self.assertEqual(history.count(), 1)

    def test_history_created_on_delete(self):
        """Test that history is created when a computer is deleted"""
        computer = Computers.objects.create(asset_tag='COMP-001')
        computer_id = computer.id
        computer.delete()

        history = AssetHistory.objects.filter(
            asset_type='Computer',
            asset_id=computer_id,
            action='deleted'
        )
        self.assertEqual(history.count(), 1)


class AssetAssignmentTests(BaseTestCase):
    """Tests for Asset Assignment workflow"""

    def test_create_assignment(self):
        """Test creating an assignment"""
        computer = Computers.objects.create(asset_tag='COMP-001')
        assignment = AssetAssignment.objects.create(
            asset_type='Computer',
            asset_id=computer.id,
            assigned_to='John Doe',
            assigned_by=self.admin_user
        )
        self.assertEqual(assignment.status, 'pending')

    def test_assignment_workflow(self):
        """Test complete assignment workflow"""
        computer = Computers.objects.create(asset_tag='COMP-001')
        assignment = AssetAssignment.objects.create(
            asset_type='Computer',
            asset_id=computer.id,
            assigned_to='John Doe',
            assigned_by=self.admin_user
        )

        # Approve
        assignment.status = 'approved'
        assignment.approved_by = self.admin_user
        assignment.save()
        self.assertEqual(assignment.status, 'approved')

        # Checkout
        assignment.status = 'checked_out'
        assignment.save()
        self.assertEqual(assignment.status, 'checked_out')

        # Return
        assignment.status = 'returned'
        assignment.save()
        self.assertEqual(assignment.status, 'returned')


class FormTests(BaseTestCase):
    """Tests for Django forms"""

    def test_computer_form_valid(self):
        """Test valid computer form"""
        form = computersForm(data={
            'asset_tag': 'COMP-001',
            'service_tag': 'SVC-001',
            'computer_name': 'TEST-PC',
            'department': 'IT',
            'user': 'John Doe',
            'make': 'Dell',
            'model': 'OptiPlex'
        })
        self.assertTrue(form.is_valid())

    def test_printer_form_valid(self):
        """Test valid printer form"""
        form = printersForm(data={
            'service_tag': 'PRT-001',
            'make': 'HP',
            'description': 'LaserJet'
        })
        self.assertTrue(form.is_valid())


class ViewTests(BaseTestCase):
    """Tests for Django views"""

    def test_home_requires_login(self):
        """Test that home page requires login"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_home_accessible_by_admin(self):
        """Test that admin can access home page"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view(self):
        """Test dashboard view"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_computer_list_view(self):
        """Test computer list view"""
        self.client.login(username='admin', password='adminpass123')
        Computers.objects.create(asset_tag='COMP-001')

        response = self.client.get(reverse('computer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'COMP-001')

    def test_computer_list_search(self):
        """Test computer list search functionality"""
        self.client.login(username='admin', password='adminpass123')
        Computers.objects.create(asset_tag='COMP-001', department='IT')
        Computers.objects.create(asset_tag='COMP-002', department='HR')

        response = self.client.get(reverse('computer_list') + '?q=IT')
        self.assertEqual(response.status_code, 200)

    def test_add_computer_view(self):
        """Test add computer view"""
        self.client.login(username='admin', password='adminpass123')

        response = self.client.post(reverse('add_computer'), {
            'asset_tag': 'COMP-NEW',
            'service_tag': 'SVC-NEW',
            'make': 'Dell'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Computers.objects.filter(asset_tag='COMP-NEW').exists())

    def test_delete_computer_view(self):
        """Test delete computer view"""
        self.client.login(username='admin', password='adminpass123')
        computer = Computers.objects.create(asset_tag='COMP-DEL')

        response = self.client.post(reverse('delete_pc', args=[computer.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Computers.objects.filter(id=computer.id).exists())

    def test_bulk_import_view(self):
        """Test bulk import view"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('bulk_import'))
        self.assertEqual(response.status_code, 200)

    def test_asset_history_view(self):
        """Test asset history view"""
        self.client.login(username='admin', password='adminpass123')
        Computers.objects.create(asset_tag='COMP-001')

        response = self.client.get(reverse('asset_history'))
        self.assertEqual(response.status_code, 200)


class ExportTests(BaseTestCase):
    """Tests for CSV export functionality"""

    def test_export_computers_csv(self):
        """Test exporting computers to CSV"""
        self.client.login(username='admin', password='adminpass123')
        Computers.objects.create(asset_tag='COMP-001', make='Dell')

        response = self.client.get(reverse('export_computers_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('COMP-001', response.content.decode())

    def test_export_printers_csv(self):
        """Test exporting printers to CSV"""
        self.client.login(username='admin', password='adminpass123')
        printers.objects.create(service_tag='PRT-001')

        response = self.client.get(reverse('export_printers_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')


class APITests(APITestCase):
    """Tests for REST API endpoints"""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_list_computers_api(self):
        """Test listing computers via API"""
        Computers.objects.create(asset_tag='COMP-001')

        response = self.client.get('/api/computers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_computer_api(self):
        """Test creating computer via API"""
        data = {
            'asset_tag': 'COMP-API',
            'service_tag': 'SVC-API',
            'make': 'Dell'
        }
        response = self.client.post('/api/computers/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Computers.objects.filter(asset_tag='COMP-API').exists())

    def test_retrieve_computer_api(self):
        """Test retrieving single computer via API"""
        computer = Computers.objects.create(asset_tag='COMP-001')

        response = self.client.get(f'/api/computers/{computer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['asset_tag'], 'COMP-001')

    def test_update_computer_api(self):
        """Test updating computer via API"""
        computer = Computers.objects.create(asset_tag='COMP-001')

        response = self.client.patch(f'/api/computers/{computer.id}/', {
            'department': 'IT'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        computer.refresh_from_db()
        self.assertEqual(computer.department, 'IT')

    def test_delete_computer_api(self):
        """Test deleting computer via API"""
        computer = Computers.objects.create(asset_tag='COMP-DEL')

        response = self.client.delete(f'/api/computers/{computer.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Computers.objects.filter(id=computer.id).exists())

    def test_computer_history_api(self):
        """Test getting computer history via API"""
        computer = Computers.objects.create(asset_tag='COMP-001')

        response = self.client.get(f'/api/computers/{computer.id}/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Created action

    def test_dashboard_api(self):
        """Test dashboard statistics API"""
        Computers.objects.create(asset_tag='COMP-001')
        printers.objects.create(service_tag='PRT-001')

        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['computer_count'], 1)
        self.assertEqual(response.data['printer_count'], 1)

    def test_assignment_workflow_api(self):
        """Test assignment workflow via API"""
        computer = Computers.objects.create(asset_tag='COMP-001')

        # Create assignment
        response = self.client.post('/api/assignments/', {
            'asset_type': 'Computer',
            'asset_id': computer.id,
            'assigned_to': 'John Doe'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assignment_id = response.data['id']

        # Approve assignment
        response = self.client.post(f'/api/assignments/{assignment_id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_filter_api(self):
        """Test search and filter in API"""
        Computers.objects.create(asset_tag='COMP-001', department='IT')
        Computers.objects.create(asset_tag='COMP-002', department='HR')

        # Search
        response = self.client.get('/api/computers/?search=IT')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        # Filter
        response = self.client.get('/api/computers/?department=HR')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_api_requires_authentication(self):
        """Test that API requires authentication"""
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/computers/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaginationTests(BaseTestCase):
    """Tests for pagination functionality"""

    def test_computer_list_pagination(self):
        """Test that computer list is paginated"""
        self.client.login(username='admin', password='adminpass123')

        # Create 30 computers
        for i in range(30):
            Computers.objects.create(asset_tag=f'COMP-{i:03d}')

        response = self.client.get(reverse('computer_list'))
        self.assertEqual(response.status_code, 200)

        # Check pagination
        self.assertTrue(hasattr(response.context['computer_items'], 'paginator'))


class SecurityTests(BaseTestCase):
    """Tests for security features"""

    def test_regular_user_cannot_access_admin_views(self):
        """Test that regular users cannot access admin views"""
        self.client.login(username='user', password='userpass123')

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_csrf_protection(self):
        """Test CSRF protection on forms"""
        self.client.login(username='admin', password='adminpass123')

        # POST without CSRF token should fail
        client = Client(enforce_csrf_checks=True)
        client.login(username='admin', password='adminpass123')

        response = client.post(reverse('add_computer'), {
            'asset_tag': 'COMP-CSRF'
        })
        self.assertEqual(response.status_code, 403)  # CSRF failure
