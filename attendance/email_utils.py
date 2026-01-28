"""
Email and Notification Utilities for CRM
Handles sending emails to crews, clients, and participants
"""
from django.core.mail import send_mass_mail, send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from .models import EmailNotification, Event
import logging

logger = logging.getLogger(__name__)


class EventCRMNotifier:
    """Handle all event-related CRM notifications and communications"""
    
    @staticmethod
    def send_event_created_notification(event):
        """Send notification when event is created"""
        try:
            # Get all event managers who should be notified
            from django.contrib.auth.models import Group
            event_managers = Group.objects.get(name='Events Manager').user_set.all()
            
            for manager in event_managers:
                if manager.email:
                    notification = EmailNotification.objects.create(
                        recipient=manager.email,
                        user=manager,
                        notification_type='event_created',
                        subject=f'New Event Created: {event.name}',
                        message=EventCRMNotifier._render_event_created_email(event, manager)
                    )
                    EventCRMNotifier._queue_email(notification)
                    
            logger.info(f"Event creation notifications queued for {event.name}")
            
        except Exception as e:
            logger.error(f"Error sending event created notification: {str(e)}")
    
    @staticmethod
    def send_event_updated_notification(event, changes):
        """Send notification when event details are updated"""
        try:
            notification = EmailNotification.objects.create(
                notification_type='event_updated',
                subject=f'Event Updated: {event.name}',
                message=EventCRMNotifier._render_event_updated_email(event, changes)
            )
            
            # Notify assigned crew about changes
            for crew in event.crew_assignments.filter(status__in=['confirmed', 'completed']):
                if crew.user.email:
                    notification.recipient = crew.user.email
                    notification.user = crew.user
                    notification.save()
                    EventCRMNotifier._queue_email(notification)
                    
            logger.info(f"Event update notifications queued for {event.name}")
            
        except Exception as e:
            logger.error(f"Error sending event updated notification: {str(e)}")
    
    @staticmethod
    def send_event_setup_briefing(event):
        """Send setup briefing/details to all crew members"""
        try:
            crew_list = event.crew_assignments.filter(status__in=['confirmed', 'completed'])
            
            for crew in crew_list:
                if crew.user.email:
                    notification = EmailNotification.objects.create(
                        recipient=crew.user.email,
                        user=crew.user,
                        notification_type='crew_assignment',
                        subject=f'Setup Briefing: {event.name}',
                        message=EventCRMNotifier._render_setup_briefing_email(event, crew)
                    )
                    EventCRMNotifier._queue_email(notification)
                    
            logger.info(f"Setup briefings sent for {event.name}")
            
        except Exception as e:
            logger.error(f"Error sending setup briefings: {str(e)}")
    
    # Email template renderers
    @staticmethod
    def _render_event_created_email(event, user):
        """Render event created email"""
        return f"""
        Dear {user.get_full_name() or user.username},
        
        A new event has been created and requires attention.
        
        Event Details:
        - Name: {event.name}
        - Date: {event.date.strftime('%d %B %Y')}
        - Location: {event.location or 'TBD'}
        - Status: {event.get_status_display()}
        
        You can assign crew and manage details in the admin panel.
        
        Best regards,
        Sound Fusion Admin
        """
    
    @staticmethod
    def _render_event_updated_email(event, changes):
        """Render event updated email"""
        changes_text = "\n".join([f"- {field}: {change}" for field, change in changes.items()])
        return f"""
        Event '{event.name}' has been updated.
        
        Changes made:
        {changes_text}
        
        Please review the changes and take any necessary action.
        
        Best regards,
        Sound Fusion Admin
        """
    
    @staticmethod
    def _render_setup_briefing_email(event, crew):
        """Render setup briefing email"""
        return f"""
        Dear {crew.user.get_full_name() or crew.user.username},
        
        Setup Briefing for: {event.name}
        Date: {event.date.strftime('%d %B %Y')}
        Location: {event.location or 'TBD'}
        Your Role: {crew.role}
        
        EVENT DETAILS:
        - Description: {event.description or 'N/A'}
        - Expected Duration: {event.duration or 'N/A'}
        - Client Contact: {event.client_contact or 'N/A'}
        
        CREW ASSIGNMENTS:
        {EventCRMNotifier._get_crew_list(event)}
        
        {f"SPECIAL INSTRUCTIONS: {crew.notes}" if crew.notes else ""}
        
        Please confirm receipt of this email and report any issues immediately.
        
        Best regards,
        Sound Fusion Team
        """
    
    @staticmethod
    def _get_crew_list(event):
        """Get formatted list of crew for briefing"""
        crew_list = event.crew_assignments.filter(status__in=['confirmed', 'completed'])
        if not crew_list:
            return "No other crew assigned yet."
        
        result = []
        for crew in crew_list:
            result.append(f"- {crew.user.get_full_name() or crew.user.username} ({crew.role})")
        return "\n".join(result)
    
    @staticmethod
    def _queue_email(notification):
        """Queue email for sending (uses console backend for now)"""
        try:
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                logger.info(f"[EMAIL] To: {notification.recipient}\nSubject: {notification.subject}\n{notification.message}")
            else:
                # For production, send actual email
                send_mail(
                    notification.subject,
                    notification.message,
                    settings.DEFAULT_FROM_EMAIL,
                    [notification.recipient],
                    fail_silently=True,
                )
                notification.is_sent = True
                notification.sent_at = timezone.now()
                notification.save()
                
        except Exception as e:
            logger.error(f"Error queuing email: {str(e)}")
    
    @staticmethod
    def send_crew_invitation(crew_assignment):
        """Send crew invitation email"""
        try:
            notification = EmailNotification.objects.create(
                recipient=crew_assignment.user.email,
                user=crew_assignment.user,
                notification_type='crew_invitation',
                subject=f'Crew Assignment: {crew_assignment.event.name}',
                message=EventCRMNotifier._render_crew_invitation_email(crew_assignment)
            )
            EventCRMNotifier._queue_email(notification)
            logger.info(f"Crew invitation sent to {crew_assignment.user.username} for {crew_assignment.event.name}")
        except Exception as e:
            logger.error(f"Error sending crew invitation: {str(e)}")
    
    @staticmethod
    def send_crew_confirmation(crew_assignment):
        """Send confirmation notification when crew accepts assignment"""
        try:
            notification = EmailNotification.objects.create(
                recipient=crew_assignment.assigned_by.email,
                user=crew_assignment.assigned_by,
                notification_type='crew_confirmed',
                subject=f'Crew Confirmed: {crew_assignment.event.name}',
                message=f"""
                Dear {crew_assignment.assigned_by.get_full_name() or crew_assignment.assigned_by.username},
                
                {crew_assignment.user.get_full_name() or crew_assignment.user.username} has confirmed their assignment for {crew_assignment.event.name}.
                
                Event: {crew_assignment.event.name}
                Date: {crew_assignment.event.date.strftime('%d %B %Y')}
                Crew Type: {crew_assignment.get_crew_type_display()}
                
                Best regards,
                Sound Fusion Team
                """
            )
            EventCRMNotifier._queue_email(notification)
        except Exception as e:
            logger.error(f"Error sending crew confirmation: {str(e)}")
    
    @staticmethod
    def send_crew_decline_notification(crew_assignment):
        """Send notification when crew declines assignment"""
        try:
            notification = EmailNotification.objects.create(
                recipient=crew_assignment.assigned_by.email,
                user=crew_assignment.assigned_by,
                notification_type='crew_declined',
                subject=f'Crew Declined: {crew_assignment.event.name}',
                message=f"""
                Dear {crew_assignment.assigned_by.get_full_name() or crew_assignment.assigned_by.username},
                
                {crew_assignment.user.get_full_name() or crew_assignment.user.username} has declined their assignment for {crew_assignment.event.name}.
                
                Event: {crew_assignment.event.name}
                Date: {crew_assignment.event.date.strftime('%d %B %Y')}
                Crew Type: {crew_assignment.get_crew_type_display()}
                
                Please find a replacement crew member.
                
                Best regards,
                Sound Fusion Team
                """
            )
            EventCRMNotifier._queue_email(notification)
        except Exception as e:
            logger.error(f"Error sending crew decline notification: {str(e)}")
    
    @staticmethod
    def _render_crew_invitation_email(crew_assignment):
        """Render crew invitation email template"""
        return f"""
        Dear {crew_assignment.user.get_full_name() or crew_assignment.user.username},
        
        You have been assigned as {crew_assignment.get_crew_type_display()} for the following event:
        
        EVENT DETAILS:
        - Event: {crew_assignment.event.name}
        - Date: {crew_assignment.event.date.strftime('%d %B %Y')}
        - Location: {crew_assignment.event.location or 'TBD'}
        - Description: {crew_assignment.event.description or 'N/A'}
        
        Please confirm or decline your assignment by logging into the system.
        
        Best regards,
        Sound Fusion Team
        """


class PaymentNotifier:
    """Handle payment-related notifications"""
    
    @staticmethod
    def send_payment_request_email(user, amount, payment_method, payment_id):
        """Send payment request to user"""
        try:
            notification = EmailNotification.objects.create(
                recipient=user.email,
                user=user,
                notification_type='payment_approved',
                subject=f'Payment Request - KSH {amount}',
                message=f"""
                Dear {user.get_full_name() or user.username},
                
                A payment has been processed for your account.
                
                Payment Details:
                - Amount: KSH {amount}
                - Method: {payment_method}
                - Reference: {payment_id}
                - Date: {timezone.now().strftime('%d %B %Y %H:%M')}
                
                If you did not authorize this payment, please contact the admin immediately.
                
                Best regards,
                Sound Fusion Admin Team
                """
            )
            
            logger.info(f"Payment request email queued for {user.username}")
            
        except Exception as e:
            logger.error(f"Error sending payment request email: {str(e)}")
