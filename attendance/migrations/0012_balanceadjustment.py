# Generated migration to update BalanceAdjustment model for tracking admin adjustments

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attendance', '0011_remove_attendancerecord_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='balanceadjustment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='balance_adjustments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='balanceadjustment',
            name='adjusted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='made_adjustments_new', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='balanceadjustment',
            name='reason',
            field=models.CharField(blank=True, default='Admin adjustment', max_length=255),
        ),
    ]
