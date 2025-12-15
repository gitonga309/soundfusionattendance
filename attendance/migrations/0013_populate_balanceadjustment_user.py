# Generated migration to populate user field from profile relationship

from django.db import migrations


def populate_user_from_profile(apps, schema_editor):
    """Populate user field from existing profile relationship"""
    BalanceAdjustment = apps.get_model('attendance', 'BalanceAdjustment')
    for adjustment in BalanceAdjustment.objects.all():
        if adjustment.profile and not adjustment.user:
            adjustment.user = adjustment.profile.user
            adjustment.save()


def reverse_populate(apps, schema_editor):
    """Reverse the population"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0012_balanceadjustment'),
    ]

    operations = [
        migrations.RunPython(populate_user_from_profile, reverse_populate),
    ]
