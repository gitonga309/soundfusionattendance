"""
Management command to fix existing attendance record times by adding 3 hours
Run with: python manage.py fix_attendance_times
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import AttendanceRecord
import datetime

class Command(BaseCommand):
    help = 'Fix attendance record times by correcting timezone offset'

    def handle(self, *args, **options):
        records = AttendanceRecord.objects.all()
        fixed_count = 0
        
        for record in records:
            # Store original time
            original_time = record.check_in_time
            
            # Create a datetime combining date and time
            dt_naive = datetime.datetime.combine(record.date, original_time)
            
            # Make it timezone aware in UTC (assuming it was stored as UTC)
            dt_utc = dt_naive.replace(tzinfo=datetime.timezone.utc)
            
            # Convert to local timezone (Africa/Nairobi)
            dt_local = dt_utc.astimezone(timezone.get_current_timezone())
            
            # Extract the corrected time
            corrected_time = dt_local.time()
            
            # Only update if time is different (to avoid unnecessary writes)
            if corrected_time != original_time:
                record.check_in_time = corrected_time
                record.save(update_fields=['check_in_time'])
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fixed {record.user.username} ({record.date}): '
                        f'{original_time} → {corrected_time}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal records fixed: {fixed_count}')
        )
