from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from attendance.models import Event, AttendanceRecord


class Command(BaseCommand):
    help = 'Create Events Manager group with limited permissions (Events + Attendance only)'

    def handle(self, *args, **options):
        # Create the group
        group, created = Group.objects.get_or_create(name='Events Manager')
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created "Events Manager" group'))
        else:
            self.stdout.write(self.style.WARNING('✓ "Events Manager" group already exists'))
        
        # Get permissions for Event and AttendanceRecord models
        event_content_type = ContentType.objects.get_for_model(Event)
        attendance_content_type = ContentType.objects.get_for_model(AttendanceRecord)
        
        # Permissions: view, add, change, delete for both models
        permissions = Permission.objects.filter(
            content_type__in=[event_content_type, attendance_content_type]
        )
        
        # Add all permissions for these two models
        group.permissions.set(permissions)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Added {permissions.count()} permissions to "Events Manager" group'))
        self.stdout.write(self.style.SUCCESS('\nPermissions assigned:'))
        for perm in permissions:
            self.stdout.write(f'  - {perm.content_type.app_label}.{perm.codename}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Setup complete!'))
        self.stdout.write(self.style.WARNING('\nTo add a user to this group:'))
        self.stdout.write('  1. Go to Django admin')
        self.stdout.write('  2. Navigate to Users')
        self.stdout.write('  3. Select the user and add them to "Events Manager" group')
