from django.contrib import admin
from .models import Profile, AttendanceRecord, Event, BalanceAdjustment, ExpenseReimbursement
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.contrib.admin import AdminSite


class LimitedEventManagerMixin:
    """
    Mixin to restrict EventAdmin and AttendanceRecordAdmin access 
    to only "Events Manager" group members
    """
    def has_add_permission(self, request):
        # Superusers always have permission
        if request.user.is_superuser:
            return True
        # Check if user is in "Events Manager" group
        return request.user.groups.filter(name="Events Manager").exists()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name="Events Manager").exists()

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name="Events Manager").exists()

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name="Events Manager").exists()

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
class AttendanceRecordAdmin(LimitedEventManagerMixin, admin.ModelAdmin):
    list_display = ('user', 'date', 'get_event', 'overtime_hours', 'amount_paid', 'is_paid')
    list_filter = ('date', 'is_paid', 'event_fk')
    search_fields = ('user__username', 'event_fk__name')
    readonly_fields = ('date',)
    
    def get_event(self, obj):
        """Display event name from event_fk"""
        return obj.event_fk.name if obj.event_fk else "No Event"
    get_event.short_description = 'Event'


@admin.register(Event)
class EventAdmin(LimitedEventManagerMixin, admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'client_venue', 'get_crew_count', 'created_by', 'created_at')
    search_fields = ('name', 'location', 'description', 'client_venue')
    list_filter = ('date', 'created_at')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    filter_horizontal = ('setup_crew', 'event_crew')  # Makes M2M selection user-friendly with widget
    
    fieldsets = (
        ('Event Details', {
            'fields': ('name', 'date', 'location', 'description')
        }),
        ('Event Logistics', {
            'fields': ('client_venue', 'setup_date', 'setup_end_date', 'equipments_delivered')
        }),
        ('Crew Assignment', {
            'fields': ('setup_crew', 'event_crew'),
            'description': '<strong>Setup Crew:</strong> Users assigned for setup/teardown work<br><strong>Event Crew:</strong> Users assigned for event day operations',
            'classes': ('wide',)
        }),
        ('System Info', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_crew_count(self, obj):
        """Show crew counts in list view"""
        setup = obj.setup_crew.count()
        event = obj.event_crew.count()
        return f"Setup: {setup} | Event: {event}"
    get_crew_count.short_description = 'Crew Assignments'

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

@admin.register(ExpenseReimbursement)
class ExpenseReimbursementAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_event', 'expense_type', 'amount', 'status', 'requested_at')
    list_filter = ('status', 'expense_type', 'requested_at', 'event')
    search_fields = ('user__username', 'event__name', 'description')
    readonly_fields = ('requested_at', 'approved_at', 'approved_by', 'receipt_photo')
    fieldsets = (
        ('Request Details', {
            'fields': ('user', 'event', 'expense_type', 'amount', 'description', 'receipt_photo')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('requested_at',),
            'classes': ('collapse',)
        }),
    )

    def get_event(self, obj):
        """Display event name"""
        return obj.event.name if obj.event else "No Event"
    get_event.short_description = 'Event'

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'approved':
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)