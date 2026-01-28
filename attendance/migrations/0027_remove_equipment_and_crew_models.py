# Generated migration to remove equipment and crew models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0026_equipment_eventprogress_equipmentmaintenance_and_more'),
    ]

    operations = [
        # Remove fields from Event model
        migrations.RemoveField(
            model_name='event',
            name='equipments_delivered',
        ),
        migrations.RemoveField(
            model_name='event',
            name='event_crew',
        ),
        migrations.RemoveField(
            model_name='event',
            name='setup_crew',
        ),
        # Delete models
        migrations.DeleteModel(
            name='Equipment',
        ),
        migrations.DeleteModel(
            name='EquipmentMaintenance',
        ),
        migrations.DeleteModel(
            name='EventCrew',
        ),
        migrations.DeleteModel(
            name='EventEquipment',
        ),
        migrations.DeleteModel(
            name='EventProgress',
        ),
    ]
