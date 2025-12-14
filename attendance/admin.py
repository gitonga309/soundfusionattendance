from django.contrib import admin
from .models import Profile, AttendanceRecord, Event, BalanceAdjustment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'email', 'balance')
    list_editable = ('balance',)
    search_fields = ('user__username', 'phone_number', 'email')
    fields = ('user', 'phone_number', 'email', 'balance', 'date_of_birth', 'disability')
    readonly_fields = ('user',)


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
    list_display = ('name', 'date', 'location', 'created_by', 'created_at')
    search_fields = ('name', 'location', 'description')
    list_filter = ('date', 'created_at')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    fields = ('name', 'date', 'location', 'description', 'created_by', 'created_at', 'updated_at')

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
