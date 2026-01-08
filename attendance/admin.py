from django.contrib import admin
from .models import Profile, AttendanceRecord, Event, BalanceAdjustment
from django.contrib.auth.models import User

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'email', 'balance')
    list_editable = ('balance',)
    search_fields = ('user__username', 'phone_number', 'email')
    fields = ('user', 'phone_number', 'email', 'balance', 'date_of_birth', 'disability')
    readonly_fields = ('user',)

    def save_model(self, request, obj, form, change):
        """Track balance changes made by admin and create BalanceAdjustment records"""
        if change and 'balance' in form.changed_data:
            # Get the old balance
            try:
                old_profile = Profile.objects.get(pk=obj.pk)
                old_balance = old_profile.balance
                new_balance = obj.balance
                
                # Calculate the difference
                adjustment_amount = new_balance - old_balance
                
                # Create a BalanceAdjustment record to track this change
                if adjustment_amount != 0:
                    BalanceAdjustment.objects.create(
                        user=obj.user,
                        amount=adjustment_amount,
                        adjusted_by=request.user,
                        reason=f"Admin adjustment via Profile page"
                    )
            except Profile.DoesNotExist:
                pass
        
        # Save the profile
        super().save_model(request, obj, form, change)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'get_event', 'overtime_hours', 'amount_paid', 'is_paid')
    list_filter = ('date', 'is_paid', 'event_fk')
    search_fields = ('user__username', 'event_fk__name')
    readonly_fields = ('date',)
    
    def get_event(self, obj):
        """Display event name from event_fk"""
        return obj.event_fk.name if obj.event_fk else "No Event"
    get_event.short_description = 'Event'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'client_venue', 'created_by', 'created_at')
    search_fields = ('name', 'location', 'description', 'client_venue')
    list_filter = ('date', 'created_at')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    fieldsets = (
        ('Event Details', {
            'fields': ('name', 'date', 'location', 'description')
        }),
        ('Event Logistics', {
            'fields': ('client_venue', 'setup_date', 'setup_end_date', 'equipments_delivered')
        }),
        ('System Info', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BalanceAdjustment)
class BalanceAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reason', 'adjusted_by', 'date')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'reason')
    readonly_fields = ('date',)
    fields = ('user', 'amount', 'reason', 'adjusted_by', 'date')

    def save_model(self, request, obj, form, change):
        if not obj.adjusted_by:
            obj.adjusted_by = request.user
        super().save_model(request, obj, form, change)
