"""
Event Progress Notification System
Handles sending client notifications about event progress updates
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class EventProgressNotifier:
    """Handles event progress notifications to clients"""
    
    STATUS_TITLES = {
        'planning': 'Event Planning Started',
        'setup_scheduled': 'Setup Scheduled',
        'setup_in_progress': 'Setup In Progress',
        'setup_complete': 'Setup Complete',
        'event_in_progress': 'Event In Progress Now',
        'event_complete': 'Event Successfully Completed',
        'teardown_in_progress': 'Teardown/Cleanup In Progress',
        'teardown_complete': 'All Done - Event Closed',
        'closed': 'Event Closed',
    }
    
    @staticmethod
    def send_status_update(event, new_status, description=""):
        """
        Send event status update to client
        
        Args:
            event: Event instance
            new_status: New status string
            description: Optional detailed description
        """
        try:
            progress = event.progress
            
            # Only send if client email is set
            if not progress.client_email:
                logger.warning(f"No client email set for event {event.id}")
                return False
            
            title = EventProgressNotifier.STATUS_TITLES.get(new_status, "Event Update")
            
            # Prepare email context
            context = {
                'event_name': event.name,
                'event_date': event.date,
                'event_location': event.client_venue or event.location,
                'status_title': title,
                'description': description or EventProgressNotifier._get_default_description(new_status),
                'status': new_status,
                'contact_email': settings.DEFAULT_FROM_EMAIL,
            }
            
            # Render email template
            subject = f"Event Update: {event.name} - {title}"
            html_message = render_to_string('attendance/emails/event_progress.html', context)
            plain_message = render_to_string('attendance/emails/event_progress.txt', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[progress.client_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Update last update sent timestamp
            progress.last_update_sent = timezone.now()
            progress.save(update_fields=['last_update_sent'])
            
            logger.info(f"Event progress email sent for {event.id} - Status: {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send event progress email for event {event.id}: {str(e)}")
            return False
    
    @staticmethod
    def send_setup_started_notification(event):
        """Notify client that setup has started"""
        from .models import EventProgress
        try:
            progress = event.progress
            progress.current_status = 'setup_in_progress'
            progress.setup_started_at = timezone.now()
            progress.save()
            
            description = (
                "Our team has started setting up for your event. "
                "We're working hard to ensure everything is perfect for your special day."
            )
            EventProgressNotifier.send_status_update(event, 'setup_in_progress', description)
        except Exception as e:
            logger.error(f"Error sending setup started notification: {str(e)}")
    
    @staticmethod
    def send_setup_complete_notification(event):
        """Notify client that setup is complete and ready for event"""
        from .models import EventProgress
        try:
            progress = event.progress
            progress.current_status = 'setup_complete'
            progress.setup_completed_at = timezone.now()
            progress.save()
            
            description = (
                "Setup is complete and all systems are tested and ready. "
                "Our team is standing by for your event."
            )
            EventProgressNotifier.send_status_update(event, 'setup_complete', description)
        except Exception as e:
            logger.error(f"Error sending setup complete notification: {str(e)}")
    
    @staticmethod
    def send_event_started_notification(event):
        """Notify client that event has started"""
        from .models import EventProgress
        try:
            progress = event.progress
            progress.current_status = 'event_in_progress'
            progress.event_started_at = timezone.now()
            progress.save()
            
            description = (
                "Your event is now live! Our team is providing full support "
                "to ensure everything runs smoothly."
            )
            EventProgressNotifier.send_status_update(event, 'event_in_progress', description)
        except Exception as e:
            logger.error(f"Error sending event started notification: {str(e)}")
    
    @staticmethod
    def send_event_completed_notification(event):
        """Notify client that event is complete and thank them"""
        from .models import EventProgress
        try:
            progress = event.progress
            progress.current_status = 'event_complete'
            progress.event_completed_at = timezone.now()
            progress.save()
            
            description = (
                "Your event was a great success! Thank you for choosing Sound Fusion. "
                "Our team is now cleaning up and will return all equipment shortly."
            )
            EventProgressNotifier.send_status_update(event, 'event_complete', description)
        except Exception as e:
            logger.error(f"Error sending event completed notification: {str(e)}")
    
    @staticmethod
    def send_custom_update(event, title, message, status=None):
        """
        Send custom update message to client
        
        Args:
            event: Event instance
            title: Update title
            message: Update message
            status: Optional status to update to
        """
        try:
            progress = event.progress
            
            if not progress.client_email:
                logger.warning(f"No client email set for event {event.id}")
                return False
            
            context = {
                'event_name': event.name,
                'event_date': event.date,
                'event_location': event.client_venue or event.location,
                'status_title': title,
                'description': message,
                'status': status or progress.current_status,
                'contact_email': settings.DEFAULT_FROM_EMAIL,
            }
            
            subject = f"Update: {event.name} - {title}"
            html_message = render_to_string('attendance/emails/event_progress.html', context)
            plain_message = render_to_string('attendance/emails/event_progress.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[progress.client_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            progress.last_update_sent = timezone.now()
            progress.save(update_fields=['last_update_sent'])
            
            logger.info(f"Custom event update sent for {event.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send custom event update: {str(e)}")
            return False
    
    @staticmethod
    def _get_default_description(status):
        """Get default description for each status"""
        descriptions = {
            'planning': "We're beginning the planning phase for your event.",
            'setup_scheduled': "Setup has been scheduled for your event.",
            'setup_in_progress': "Our team is currently setting up for your event.",
            'setup_complete': "Setup is complete and we're ready for your event.",
            'event_in_progress': "Your event is currently happening.",
            'event_complete': "Your event has been successfully completed.",
            'teardown_in_progress': "We're cleaning up after your event.",
            'teardown_complete': "All cleanup is complete.",
            'closed': "Your event has been closed.",
        }
        return descriptions.get(status, "Event status has been updated.")


class EventProgressEmailTemplates:
    """Helper class for email template content"""
    
    @staticmethod
    def get_html_template():
        """Return HTML email template for event progress"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 20px; border-radius: 5px 5px 0 0; }
                .content { background: #f9f9f9; padding: 20px; border-left: 4px solid #667eea; }
                .footer { background: #f0f0f0; padding: 15px; font-size: 12px; color: #666; }
                .status-badge { 
                    display: inline-block; 
                    background: #667eea; 
                    color: white; 
                    padding: 5px 15px; 
                    border-radius: 20px;
                    font-size: 12px;
                    margin: 10px 0;
                }
                .event-details { margin: 20px 0; }
                .detail-row { margin: 10px 0; }
                .detail-label { font-weight: bold; color: #667eea; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ status_title }}</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    
                    <p>{{ description }}</p>
                    
                    <div class="event-details">
                        <div class="detail-row">
                            <span class="detail-label">Event:</span> {{ event_name }}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Date:</span> {{ event_date|date:"F d, Y" }}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Location:</span> {{ event_location }}
                        </div>
                        <div class="detail-row">
                            <span class="status-badge">{{ status }}</span>
                        </div>
                    </div>
                    
                    <p>If you have any questions or concerns, please don't hesitate to contact us.</p>
                    
                    <p>Best regards,<br/>
                    <strong>Sound Fusion Team</strong></p>
                </div>
                <div class="footer">
                    <p>© 2024 Sound Fusion. All rights reserved.</p>
                    <p>Contact: {{ contact_email }}</p>
                </div>
            </div>
        </body>
        </html>
        """
