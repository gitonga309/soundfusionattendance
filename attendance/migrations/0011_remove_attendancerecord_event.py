# Generated migration to remove old event CharField

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0010_attendancerecord_event_fk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendancerecord',
            name='event',
        ),
    ]
