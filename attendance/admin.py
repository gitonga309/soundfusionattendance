#from django.contrib import admin

# Register your models here.
#from .models import AttendanceRecord,Profile

#admin.site.register(AttendanceRecord)
#admin.site.register(Profile)
from django.contrib import admin
from .models import Profile, AttendanceRecord,BalanceAdjustment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'email', 'balance')
    list_editable = ('balance',)
    search_fields = ('user__username', 'phone_number', 'email')
    fields = ('user', 'phone_number', 'email', 'balance', 'date_of_birth', 'disability')
    readonly_fields = ('user',)

    def save_model(self, request, obj, form, change):
        if 'balance' in form.changed_data:
            old_balance = Profile.objects.get(pk=obj.pk).balance if obj.pk else 0
            new_balance = obj.balance
            diff = new_balance - old_balance
            if diff != 0:
                BalanceAdjustment.objects.create(
                    profile=obj,
                    admin=request.user,
                    amount=diff,
                    reason="Manual admin adjustment"
                )
        super().save_model(request, obj, form, change)

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'event', 'overtime_hours', 'amount_paid', 'is_paid', 'admin_adjustment')
    list_editable = ('is_paid', 'admin_adjustment')
    search_fields = ('user__username', 'event')

    def save_model(self, request, obj, form, change):
        """
        When admin marks attendance as paid or changes admin_adjustment,
        update the user's Profile balance automatically.
        """
        super().save_model(request, obj, form, change)

        # Update balance only after the record is saved
        profile, _ = Profile.objects.get_or_create(user=obj.user)

        if obj.is_paid:
            # If admin marks as paid → reduce balance
            profile.balance -= obj.amount_paid
        else:
            # Otherwise, adjust the balance with admin_adjustment if given
            profile.balance += obj.admin_adjustment

        # Ensure no negative balance
        if profile.balance < 0:
            profile.balance = 0

        profile.save()
