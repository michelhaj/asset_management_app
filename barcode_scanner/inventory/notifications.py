"""
Email notification utilities for the Asset Management System
"""
import logging
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.models import User

from .models import (
    Computers, printers, monitors, docking_stations,
    AssetAssignment, NotificationSetting
)

logger = logging.getLogger(__name__)


def send_warranty_expiry_notifications():
    """
    Send email notifications for assets with warranties expiring soon.
    Should be run daily via a cron job or Celery task.
    """
    today = timezone.now().date()
    reminder_days = getattr(settings, 'WARRANTY_REMINDER_DAYS', 30)
    expiry_date = today + timedelta(days=reminder_days)

    # Get users who want warranty notifications
    users_with_notifications = User.objects.filter(
        notificationsetting__email_on_warranty_expiry=True
    ).select_related('notificationsetting')

    if not users_with_notifications.exists():
        logger.info("No users configured for warranty notifications")
        return

    # Collect expiring assets
    expiring_assets = {
        'computers': list(Computers.objects.filter(
            warranty_expiry__lte=expiry_date,
            warranty_expiry__gte=today
        ).values('id', 'asset_tag', 'make', 'model', 'warranty_expiry')),
        'printers': list(printers.objects.filter(
            warranty_expiry__lte=expiry_date,
            warranty_expiry__gte=today
        ).values('id', 'service_tag', 'make', 'warranty_expiry')),
        'monitors': list(monitors.objects.filter(
            warranty_expiry__lte=expiry_date,
            warranty_expiry__gte=today
        ).values('id', 'asset_tag', 'make', 'warranty_expiry')),
        'docking_stations': list(docking_stations.objects.filter(
            warranty_expiry__lte=expiry_date,
            warranty_expiry__gte=today
        ).values('id', 'asset_tag', 'make', 'warranty_expiry')),
    }

    total_expiring = sum(len(assets) for assets in expiring_assets.values())

    if total_expiring == 0:
        logger.info("No assets with expiring warranties")
        return

    # Send notifications to each user
    for user in users_with_notifications:
        try:
            user_reminder_days = user.notificationsetting.warranty_reminder_days
            user_expiry_date = today + timedelta(days=user_reminder_days)

            # Filter assets based on user's preference
            user_expiring = {
                'computers': [a for a in expiring_assets['computers']
                             if a['warranty_expiry'] <= user_expiry_date],
                'printers': [a for a in expiring_assets['printers']
                            if a['warranty_expiry'] <= user_expiry_date],
                'monitors': [a for a in expiring_assets['monitors']
                            if a['warranty_expiry'] <= user_expiry_date],
                'docking_stations': [a for a in expiring_assets['docking_stations']
                                    if a['warranty_expiry'] <= user_expiry_date],
            }

            user_total = sum(len(assets) for assets in user_expiring.values())
            if user_total == 0:
                continue

            context = {
                'user': user,
                'expiring_assets': user_expiring,
                'total_expiring': user_total,
                'reminder_days': user_reminder_days,
            }

            subject = f'Asset Warranty Expiry Alert: {user_total} assets expiring soon'
            message = render_to_string('emails/warranty_expiry.txt', context)
            html_message = render_to_string('emails/warranty_expiry.html', context)

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )

            logger.info(f"Sent warranty notification to {user.email}")

        except Exception as e:
            logger.error(f"Failed to send warranty notification to {user.email}: {e}")


def send_assignment_notification(assignment, action='created'):
    """
    Send email notification for asset assignment actions.

    Args:
        assignment: AssetAssignment instance
        action: 'created', 'approved', 'rejected', 'checked_out', 'returned'
    """
    if not assignment.assigned_by or not assignment.assigned_by.email:
        logger.warning(f"No email for assignment {assignment.id}")
        return

    # Check user notification preferences
    try:
        notification_setting = NotificationSetting.objects.get(
            user=assignment.assigned_by
        )
        if not notification_setting.email_on_assignment:
            return
    except NotificationSetting.DoesNotExist:
        pass  # Default to sending notification

    subject_templates = {
        'created': f'Asset Assignment Created: {assignment.asset_type} {assignment.asset_id}',
        'approved': f'Asset Assignment Approved: {assignment.asset_type} {assignment.asset_id}',
        'rejected': f'Asset Assignment Rejected: {assignment.asset_type} {assignment.asset_id}',
        'checked_out': f'Asset Checked Out: {assignment.asset_type} {assignment.asset_id}',
        'returned': f'Asset Returned: {assignment.asset_type} {assignment.asset_id}',
    }

    subject = subject_templates.get(action, f'Asset Assignment Update: {assignment.asset_id}')

    context = {
        'assignment': assignment,
        'action': action,
    }

    try:
        message = render_to_string('emails/assignment_notification.txt', context)
        html_message = render_to_string('emails/assignment_notification.html', context)

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[assignment.assigned_by.email],
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f"Sent assignment notification to {assignment.assigned_by.email}")

    except Exception as e:
        logger.error(f"Failed to send assignment notification: {e}")


def send_daily_summary():
    """
    Send daily summary email to admins.
    Should be run daily via a cron job or Celery task.
    """
    users_with_daily_summary = User.objects.filter(
        notificationsetting__daily_summary=True
    )

    if not users_with_daily_summary.exists():
        return

    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Gather statistics
    stats = {
        'computers_total': Computers.objects.count(),
        'printers_total': printers.objects.count(),
        'monitors_total': monitors.objects.count(),
        'docking_stations_total': docking_stations.objects.count(),
        'computers_added_today': Computers.objects.filter(
            created_at__date=yesterday
        ).count(),
        'pending_assignments': AssetAssignment.objects.filter(
            status='pending'
        ).count(),
    }

    context = {
        'stats': stats,
        'date': yesterday,
    }

    for user in users_with_daily_summary:
        try:
            context['user'] = user

            subject = f'Asset Management Daily Summary - {yesterday}'
            message = render_to_string('emails/daily_summary.txt', context)
            html_message = render_to_string('emails/daily_summary.html', context)

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )

            logger.info(f"Sent daily summary to {user.email}")

        except Exception as e:
            logger.error(f"Failed to send daily summary to {user.email}: {e}")


def send_weekly_summary():
    """
    Send weekly summary email to users who requested it.
    Should be run weekly via a cron job or Celery task.
    """
    users_with_weekly_summary = User.objects.filter(
        notificationsetting__weekly_summary=True
    )

    if not users_with_weekly_summary.exists():
        return

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Gather statistics
    stats = {
        'computers_total': Computers.objects.count(),
        'printers_total': printers.objects.count(),
        'monitors_total': monitors.objects.count(),
        'docking_stations_total': docking_stations.objects.count(),
        'computers_added_week': Computers.objects.filter(
            created_at__date__gte=week_ago
        ).count(),
        'assignments_completed': AssetAssignment.objects.filter(
            status='returned',
            returned_date__date__gte=week_ago
        ).count(),
    }

    context = {
        'stats': stats,
        'start_date': week_ago,
        'end_date': today,
    }

    for user in users_with_weekly_summary:
        try:
            context['user'] = user

            subject = f'Asset Management Weekly Summary - Week of {week_ago}'
            message = render_to_string('emails/weekly_summary.txt', context)
            html_message = render_to_string('emails/weekly_summary.html', context)

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )

            logger.info(f"Sent weekly summary to {user.email}")

        except Exception as e:
            logger.error(f"Failed to send weekly summary to {user.email}: {e}")
