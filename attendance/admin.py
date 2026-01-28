from django.contrib import admin
from .models import (
    Profile, AttendanceRecord, Event, BalanceAdjustment, ExpenseReimbursement, 
    SalaryPayment, EmployeeOnboarding, PaymentRecord, EmailNotification, 
    MpesaPayment
)
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.contrib.admin import AdminSite
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django import forms
from django.urls import reverse
from django.utils.html import format_html
from .mpesa_utils import MpesaClient
from .email_utils import EventCRMNotifier


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
    list_display = ('user', 'phone_number', 'email', 'employment_type', 'job_role', 'balance', 'send_stk_push_button')
    list_filter = ('employment_type', 'job_role')
    list_editable = ('balance',)
    search_fields = ('user__username', 'phone_number', 'email')
    change_list_template = 'admin/attendance/profile/change_list.html'
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'phone_number', 'email')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'disability')
        }),
        ('Employment', {
            'fields': ('employment_type', 'job_role', 'monthly_salary'),
            'description': 'Select employment type. For salaried employees, specify the job role and monthly salary.'
        }),
        ('Financial', {
            'fields': ('balance',),
            'description': 'User\'s current balance (sum of unpaid attendance, reimbursements, and salary payments)'
        }),
    )
    
    readonly_fields = ('user',)

    def changelist_view(self, request, extra_context=None):
        """Add total balance to the changelist view"""
        from django.db.models import Sum
        
        extra_context = extra_context or {}
        
        # Calculate total balance across all users
        total_balance = Profile.objects.aggregate(total=Sum('balance'))['total'] or 0
        
        extra_context['total_balance'] = float(total_balance)
        extra_context['total_users'] = Profile.objects.count()
        
        return super().changelist_view(request, extra_context=extra_context)

    def send_stk_push_button(self, obj):
        """Display STK push button in list view"""
        if obj.phone_number:
            return format_html(
                '<a class="button" style="background-color: #417690; pointer-events: none; opacity: 0.5; cursor: not-allowed;" disabled>Send STK</a>'
            )
        return "No phone"
    send_stk_push_button.short_description = 'Send Payment'

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
    list_display = ('get_user_link', 'date', 'get_event', 'get_employment_type', 'overtime_hours', 'amount_paid', 'get_history_link')
    list_filter = ('date', 'event_fk', 'user__profile__employment_type')
    search_fields = ('user__username', 'event_fk__name')
    readonly_fields = ('date',)
    
    fieldsets = (
        ('Attendance Info', {
            'fields': ('user', 'date', 'check_in_time', 'event_fk', 'get_employment_type')
        }),
        ('Work Details', {
            'fields': ('overtime_hours', 'amount_paid'),
            'description': 'Overtime hours and amount owed'
        }),
        ('Payment Status', {
            'fields': ('admin_adjustment',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_link(self, obj):
        """Display user name as clickable link to filtered attendance records"""
        from django.utils.html import format_html
        from django.urls import reverse
        
        user_records_url = reverse('admin:attendance_attendancerecord_changelist') + f"?user__id__exact={obj.user.id}"
        return format_html(
            '<a href="{}">{}</a>',
            user_records_url,
            obj.user.get_full_name() or obj.user.username
        )
    get_user_link.short_description = 'User'
    
    def get_event(self, obj):
        """Display event name from event_fk"""
        return obj.event_fk.name if obj.event_fk else "No Event"
    get_event.short_description = 'Event'
    
    def get_employment_type(self, obj):
        """Display employment type"""
        return obj.user.profile.get_employment_type_display()
    get_employment_type.short_description = 'Employment Type'
    
    def amount_paid(self, obj):
        """Display amount owed"""
        return f"KSH {obj.amount_paid}"
    amount_paid.short_description = 'Amount'
    
    def get_history_link(self, obj):
        """Display link to view balance adjustment history for user"""
        from django.utils.html import format_html
        from django.urls import reverse
        
        history_url = reverse('admin:attendance_balanceadjustment_changelist') + f"?user__id__exact={obj.user.id}"
        return format_html(
            '<a class="button" href="{}" style="background: #417690; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none;">Changes History</a>',
            history_url
        )
    get_history_link.short_description = 'Changes History'


@admin.register(Event)
class EventAdmin(LimitedEventManagerMixin, admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'client_venue', 'created_by', 'created_at')
    search_fields = ('name', 'location', 'description', 'client_venue')
    list_filter = ('date', 'created_at')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    filter_horizontal = ('setup_crew', 'event_crew')
    
    fieldsets = (
        ('Event Details', {
            'fields': ('name', 'date', 'location', 'description')
        }),
        ('Event Logistics', {
            'fields': ('client_venue', 'setup_date', 'setup_end_date')
        }),
        ('Crew Assignments', {
            'fields': ('setup_crew', 'event_crew'),
            'description': 'Use the arrows to assign crew members to setup and event day'
        }),
        ('System Info', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """Customize form to change setup_end_date label to 'Set Down Date'"""
        form = super().get_form(request, obj, **kwargs)
        if 'setup_end_date' in form.base_fields:
            form.base_fields['setup_end_date'].label = 'Set Down Date'
        return form

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
    list_display = ('user', 'get_event', 'expense_type', 'amount', 'status', 'is_paid', 'send_stk_button', 'requested_at')
    list_filter = ('status', 'expense_type', 'requested_at', 'event', 'is_paid')
    list_editable = ('status', 'is_paid')
    search_fields = ('user__username', 'event__name', 'description')
    readonly_fields = ('requested_at', 'approved_at', 'approved_by', 'receipt_photo_display')
    change_list_template = 'admin/attendance/expensereimbursement/change_list.html'
    
    fieldsets = (
        ('Request Details', {
            'fields': ('user', 'event', 'expense_type', 'amount', 'description', 'receipt_photo', 'receipt_photo_display')
        }),
        ('Status & Approval', {
            'fields': ('status', 'is_paid', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('requested_at',),
            'classes': ('collapse',)
        }),
    )
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Use a dropdown select widget for is_paid field instead of checkbox"""
        if db_field.name == 'is_paid':
            # Create a custom select widget
            kwargs['widget'] = forms.Select(choices=[
                (True, 'Paid'),
                (False, 'Not Paid'),
            ])
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    def changelist_view(self, request, extra_context=None):
        """Handle both GET and POST requests for bulk updates and show totals"""
        from django.http import JsonResponse
        import json
        from django.db.models import Sum, Q
        
        # Handle AJAX POST for bulk updates
        if request.method == 'POST' and 'application/json' in request.META.get('CONTENT_TYPE', ''):
            try:
                data = json.loads(request.body)
                changes = data.get('changes', [])
                
                for change in changes:
                    try:
                        reimbursement = ExpenseReimbursement.objects.get(pk=change['id'])
                        new_status = change.get('status', reimbursement.status)
                        new_paid_status = change.get('paid_status', 'Not Paid')
                        new_is_paid = new_paid_status == 'Paid'
                        
                        # Update status if it changed
                        if new_status != reimbursement.status:
                            reimbursement.status = new_status
                            if new_status == 'approved' and not reimbursement.approved_by:
                                reimbursement.approved_by = request.user
                                reimbursement.approved_at = timezone.now()
                                # Update user balance when approved
                                profile = reimbursement.user.profile
                                profile.balance += reimbursement.amount
                                profile.save()
                                # Create balance adjustment record
                                BalanceAdjustment.objects.create(
                                    user=reimbursement.user,
                                    reason=f"Reimbursement approved: {reimbursement.get_expense_type_display()} - KSH {reimbursement.amount}",
                                    amount=reimbursement.amount,
                                    adjusted_by=request.user
                                )
                        
                        # Update paid status if changed
                        if new_is_paid != reimbursement.is_paid:
                            reimbursement.is_paid = new_is_paid
                        
                        reimbursement.save()
                    except ExpenseReimbursement.DoesNotExist:
                        pass
                
                return JsonResponse({'success': True, 'message': 'All changes saved successfully!'})
            except Exception as e:
                import traceback
                return JsonResponse({'success': False, 'error': str(e), 'traceback': traceback.format_exc()})
        
        # Calculate totals for display
        all_reimbursements = ExpenseReimbursement.objects.all()
        
        total_requested = all_reimbursements.aggregate(Sum('amount'))['amount__sum'] or 0
        total_approved = all_reimbursements.filter(status='approved').aggregate(Sum('amount'))['amount__sum'] or 0
        total_paid = all_reimbursements.filter(is_paid=True).aggregate(Sum('amount'))['amount__sum'] or 0
        total_pending = all_reimbursements.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Add extra context with totals
        extra_context = extra_context or {}
        extra_context['total_requested'] = f"KSH {total_requested:,.2f}"
        extra_context['total_approved'] = f"KSH {total_approved:,.2f}"
        extra_context['total_paid'] = f"KSH {total_paid:,.2f}"
        extra_context['total_pending'] = f"KSH {total_pending:,.2f}"
        
        # For GET requests, use parent implementation
        return super().changelist_view(request, extra_context)

    def get_event(self, obj):
        """Display event name"""
        return obj.event.name if obj.event else "—"
    get_event.short_description = 'Event'

    def send_stk_button(self, obj):
        """Display STK push button for sending payment"""
        if obj.user.profile.phone_number and obj.is_paid == False and obj.status == 'approved':
            return format_html(
                '<a class="button" style="background-color: #417690; pointer-events: none; opacity: 0.5; cursor: not-allowed;" disabled>Send STK</a>'
            )
        return "—"
    send_stk_button.short_description = 'Send Payment'

    def receipt_photo_display(self, obj):
        """Display receipt photo as a clickable link and preview"""
        if obj.receipt_photo:
            from django.utils.html import format_html
            image_url = obj.receipt_photo.url
            return format_html(
                '<div><img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 4px;"/>'
                '<br><br><a href="{}" target="_blank" style="color: #2ecc71; text-decoration: none;"><i class="fas fa-download"></i> Download Full Image</a></div>',
                image_url,
                image_url
            )
        return "No receipt uploaded"
    receipt_photo_display.short_description = "Receipt Photo Preview"

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'approved':
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
            # Note: Reimbursements are refunds and should not affect user balance
        super().save_model(request, obj, form, change)



@admin.register(SalaryPayment)
class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'month_year', 'base_salary', 'overtime_pay', 'supper_allowance', 'total_amount', 'paid_by')
    list_filter = ('month_year', 'user')
    search_fields = ('user__username',)
    readonly_fields = ('paid_at',)
    
    fieldsets = (
        ('Employee', {
            'fields': ('user',)
        }),
        ('Salary Breakdown', {
            'fields': ('month_year', 'base_salary', 'overtime_pay', 'supper_allowance', 'total_amount'),
            'description': 'Base salary + overtime + supper allowance'
        }),
        ('Payment Info', {
            'fields': ('paid_by', 'paid_at', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """If editing existing salary, lock down base_salary and month_year"""
        if obj:
            return self.readonly_fields + ['month_year', 'base_salary']
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Auto-calculate total_amount and track who processed the payment"""
        if not obj.paid_by:
            obj.paid_by = request.user
        
        # Auto-calculate total amount
        obj.total_amount = obj.base_salary + obj.overtime_pay + obj.supper_allowance
        
        super().save_model(request, obj, form, change)


@admin.register(EmployeeOnboarding)
class EmployeeOnboardingAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_status_badge', 'job_role', 'monthly_salary', 'email', 'submitted_at')
    list_filter = ('status', 'job_role', 'submitted_at')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('submitted_at', 'reviewed_at', 'reviewed_by', 'get_profile_status', 'user')
    date_hierarchy = 'submitted_at'
    ordering = ('-submitted_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'national_id')
        }),
        ('Employment Details', {
            'fields': ('job_role', 'monthly_salary', 'bank_account'),
            'description': 'Specify the job role and monthly salary for the salaried position'
        }),
        ('Documents', {
            'fields': ('id_photo', 'employment_letter', 'bank_details')
        }),
        ('Approval Status', {
            'fields': ('status', 'rejection_reason'),
            'description': 'Change status to approve or reject the application<br><strong>Workflow:</strong> pending → accepted → completed'
        }),
        ('Profile Information', {
            'fields': ('get_profile_status',),
            'description': 'System-generated profile information (read-only). Shows when user account and profile are created.'
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'submitted_at', 'reviewed_at'),
            'classes': ('collapse',),
            'description': 'Admin who reviewed and timestamps'
        }),
        ('User Account', {
            'fields': ('user',),
            'classes': ('collapse',),
            'description': 'Auto-created user account. Activated when status → "completed"'
        }),
    )
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Full Name'
    
    def get_status_badge(self, obj):
        """Display color-coded status badge"""
        from django.utils.html import format_html
        
        status_colors = {
            'pending': '#FFC107',      # Yellow/Orange
            'accepted': '#17A2B8',     # Blue
            'completed': '#6C757D',    # Grey
            'rejected': '#DC3545',     # Red
        }
        color = status_colors.get(obj.status, '#6C757D')
        
        status_labels = {
            'pending': 'Pending Review',
            'accepted': 'Accepted',
            'completed': 'Completed',
            'rejected': 'Rejected',
        }
        label = status_labels.get(obj.status, obj.status)
        
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            label
        )
    get_status_badge.short_description = 'Status'
    
    def get_profile_status(self, obj):
        """Check if Profile already exists"""
        from django.utils.html import format_html
        
        if not obj.user:
            return format_html(
                '<span style="color: #999;">⚠️ No user account yet</span>'
            )
        
        try:
            profile = Profile.objects.get(user=obj.user)
            salary = profile.monthly_salary or 0
            balance = profile.balance or 0
            return format_html(
                '<div style="background: #e7f3ff; padding: 10px; border-left: 4px solid #2ecc71; border-radius: 3px;">'
                '<strong>✓ Profile Created</strong><br>'
                '💰 Monthly Salary: KSH {:,.0f}<br>'
                '📊 Current Balance: KSH {:,.0f}<br>'
                '👤 Status: {}'
                '</div>',
                salary,
                balance,
                profile.get_employment_type_display()
            )
        except Profile.DoesNotExist:
            return format_html(
                '<span style="color: #DC3545;">✗ No Profile yet</span>'
            )
    get_profile_status.short_description = 'Employee Profile Status'
    
    def changelist_view(self, request, extra_context=None):
        """Add statistics to the changelist view"""
        from django.db.models import Sum
        
        extra_context = extra_context or {}
        
        # Count by status
        pending_count = EmployeeOnboarding.objects.filter(status='pending').count()
        accepted_count = EmployeeOnboarding.objects.filter(status='accepted').count()
        completed_count = EmployeeOnboarding.objects.filter(status='completed').count()
        rejected_count = EmployeeOnboarding.objects.filter(status='rejected').count()
        
        # Total active salaried employees
        active_salaried = Profile.objects.filter(employment_type='salaried').count()
        total_salary_budget = Profile.objects.filter(employment_type='salaried').aggregate(total=Sum('monthly_salary'))['total'] or 0
        
        extra_context['pending_count'] = pending_count
        extra_context['accepted_count'] = accepted_count
        extra_context['completed_count'] = completed_count
        extra_context['rejected_count'] = rejected_count
        extra_context['active_salaried'] = active_salaried
        extra_context['total_salary_budget'] = float(total_salary_budget)
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def save_model(self, request, obj, form, change):
        """Enhanced approval logic with better workflow"""
        
        # Track status changes
        old_status = None
        if change:
            try:
                old_obj = EmployeeOnboarding.objects.get(pk=obj.pk)
                old_status = old_obj.status
            except EmployeeOnboarding.DoesNotExist:
                pass
        
        # ACCEPTANCE LOGIC: pending → accepted
        # When admin marks as 'accepted', create the user account and Profile
        if obj.status == 'accepted' and old_status != 'accepted':
            # Create user account if doesn't exist
            if not obj.user:
                # Generate a username from email
                username_base = obj.email.split('@')[0]
                username = username_base
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{username_base}{counter}"
                    counter += 1
                
                # Create user with initial password
                user = User.objects.create_user(
                    username=username,
                    email=obj.email,
                    first_name=obj.first_name,
                    last_name=obj.last_name,
                    is_active=False  # Will be activated when 'completed'
                )
                obj.user = user
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
            
            # Create/Update Profile with salaried info
            if obj.user:
                profile, created = Profile.objects.get_or_create(user=obj.user)
                profile.employment_type = 'salaried'
                profile.job_role = obj.job_role
                profile.monthly_salary = obj.monthly_salary
                profile.phone_number = obj.phone_number
                profile.date_of_birth = obj.date_of_birth
                profile.email = obj.email
                profile.save()
        
        # COMPLETION LOGIC: accepted → completed
        # When admin marks as 'completed', activate the user account
        if obj.status == 'completed' and old_status != 'completed':
            if obj.user:
                # Activate the user account
                obj.user.is_active = True
                obj.user.first_name = obj.first_name
                obj.user.last_name = obj.last_name
                obj.user.email = obj.email
                obj.user.save()
                
                # Ensure Profile exists with latest info
                profile, created = Profile.objects.get_or_create(user=obj.user)
                profile.employment_type = 'salaried'
                profile.job_role = obj.job_role
                profile.monthly_salary = obj.monthly_salary
                profile.phone_number = obj.phone_number
                profile.date_of_birth = obj.date_of_birth
                profile.email = obj.email
                profile.balance = 0  # Start with zero balance
                profile.save()
                
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
        
        # REJECTION LOGIC: Any status → rejected
        # When admin marks as 'rejected', deactivate the user account
        if obj.status == 'rejected' and old_status != 'rejected':
            if obj.user:
                obj.user.is_active = False
                obj.user.save()
            
            if not obj.rejection_reason:
                obj.rejection_reason = "Rejected by admin"
            
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        
        super().save_model(request, obj, form, change)

    
    def changelist_view(self, request, extra_context=None):
        """Add statistics to the changelist view"""
        from django.db.models import Sum
        
        extra_context = extra_context or {}
        
        # Count by status
        pending_count = EmployeeOnboarding.objects.filter(status='pending').count()
        accepted_count = EmployeeOnboarding.objects.filter(status='accepted').count()
        completed_count = EmployeeOnboarding.objects.filter(status='completed').count()
        rejected_count = EmployeeOnboarding.objects.filter(status='rejected').count()
        
        # Total active salaried employees
        active_salaried = Profile.objects.filter(employment_type='salaried').count()
        total_salary_budget = Profile.objects.filter(employment_type='salaried').aggregate(total=Sum('monthly_salary'))['total'] or 0
        
        extra_context['pending_count'] = pending_count
        extra_context['accepted_count'] = accepted_count
        extra_context['completed_count'] = completed_count
        extra_context['rejected_count'] = rejected_count
        extra_context['active_salaried'] = active_salaried
        extra_context['total_salary_budget'] = float(total_salary_budget)
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def save_model(self, request, obj, form, change):
        """Enhanced approval logic with better workflow"""
        
        # Track status changes
        old_status = None
        if change:
            try:
                old_obj = EmployeeOnboarding.objects.get(pk=obj.pk)
                old_status = old_obj.status
            except EmployeeOnboarding.DoesNotExist:
                pass
        
        # ACCEPTANCE LOGIC: pending → accepted
        # When admin marks as 'accepted', create the user account and Profile
        if obj.status == 'accepted' and old_status != 'accepted':
            # Create user account if doesn't exist
            if not obj.user:
                # Generate a username from email
                username_base = obj.email.split('@')[0]
                username = username_base
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{username_base}{counter}"
                    counter += 1
                
                # Create user with initial password
                user = User.objects.create_user(
                    username=username,
                    email=obj.email,
                    first_name=obj.first_name,
                    last_name=obj.last_name,
                    is_active=False  # Will be activated when 'completed'
                )
                obj.user = user
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
            
            # Create/Update Profile with salaried info
            if obj.user:
                profile, created = Profile.objects.get_or_create(user=obj.user)
                profile.employment_type = 'salaried'
                profile.job_role = obj.job_role
                profile.monthly_salary = obj.monthly_salary
                profile.phone_number = obj.phone_number
                profile.date_of_birth = obj.date_of_birth
                profile.email = obj.email
                profile.save()
        
        # COMPLETION LOGIC: accepted → completed
        # When admin marks as 'completed', activate the user account
        if obj.status == 'completed' and old_status != 'completed':
            if obj.user:
                # Activate the user account
                obj.user.is_active = True
                obj.user.first_name = obj.first_name
                obj.user.last_name = obj.last_name
                obj.user.email = obj.email
                obj.user.save()
                
                # Ensure Profile exists with latest info
                profile, created = Profile.objects.get_or_create(user=obj.user)
                profile.employment_type = 'salaried'
                profile.job_role = obj.job_role
                profile.monthly_salary = obj.monthly_salary
                profile.phone_number = obj.phone_number
                profile.date_of_birth = obj.date_of_birth
                profile.email = obj.email
                profile.balance = 0  # Start with zero balance
                profile.save()
                
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
        
        # REJECTION LOGIC: Any status → rejected
        # When admin marks as 'rejected', deactivate the user account
        if obj.status == 'rejected' and old_status != 'rejected':
            if obj.user:
                obj.user.is_active = False
                obj.user.save()
            
            if not obj.rejection_reason:
                obj.rejection_reason = "Rejected by admin"
            
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        
        super().save_model(request, obj, form, change)


# ========== CUSTOM USER ADMIN ==========

class CustomUserAdmin(admin.ModelAdmin):
    """Enhanced User admin with Events Manager creation features"""
    list_display = ('username', 'email', 'get_groups', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = (
        ('Account Info', {
            'fields': ('username', 'password', 'email')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
            'description': '💡 <strong>Tip:</strong> Add user to "Events Manager" group to restrict them to Events & Attendance only. Staff status is set automatically.',
            'classes': ('wide',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
    filter_horizontal = ('groups',)

    def get_groups(self, obj):
        """Display user's groups"""
        groups = obj.groups.all()
        if groups:
            return ', '.join([g.name for g in groups])
        return '—'
    get_groups.short_description = 'Groups'
    
    def save_model(self, request, obj, form, change):
        """Save user and auto-enable staff if added to Events Manager"""
        super().save_model(request, obj, form, change)


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'reference_number', 'payment_date')
    list_filter = ('payment_method', 'payment_date', 'user')
    search_fields = ('user__username', 'reference_number')
    readonly_fields = ('payment_date',)
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('user', 'amount', 'payment_method', 'reference_number')
        }),
        ('Additional Info', {
            'fields': ('notes', 'payment_date'),
            'classes': ('collapse',)
        }),
    )


# ============= M-PESA PAYMENT ADMIN =============
@admin.register(MpesaPayment)
class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'amount', 'status', 'payment_purpose', 'initiated_at', 'stk_push_button')
    list_filter = ('status', 'initiated_at')
    search_fields = ('user__username', 'phone_number', 'checkout_request_id')
    readonly_fields = ('checkout_request_id', 'merchant_request_id', 'receipt_number', 'transaction_date', 'initiated_at', 'completed_at', 'result_code', 'result_description')
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('user', 'phone_number', 'amount', 'payment_purpose', 'status')
        }),
        ('M-Pesa Details', {
            'fields': ('checkout_request_id', 'merchant_request_id', 'receipt_number', 'result_code', 'result_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('initiated_at', 'completed_at', 'transaction_date'),
            'classes': ('collapse',)
        }),
    )
    
    def stk_push_button(self, obj):
        """Display button to resend STK push if payment is pending"""
        if obj.status == 'pending':
            return format_html(
                '<a class="button" style="pointer-events: none; opacity: 0.5; cursor: not-allowed;" disabled>Resend STK Push</a>'
            )
        return '—'
    stk_push_button.short_description = 'Action'
    
    actions = ['initiate_stk_push_action']
    
    def initiate_stk_push_action(self, request, queryset):
        """Admin action to initiate STK push"""
        mpesa = MpesaClient()
        for payment in queryset.filter(status='initiated'):
            try:
                result = mpesa.initiate_stk_push(
                    payment.user,
                    payment.phone_number,
                    payment.amount,
                    payment.payment_purpose,
                    payment.id
                )
                if result['success']:
                    payment.checkout_request_id = result['checkout_request_id']
                    payment.merchant_request_id = result['merchant_request_id']
                    payment.status = 'pending'
                    payment.save()
                    self.message_user(request, f"STK push initiated for {payment.user.username}")
                else:
                    self.message_user(request, f"Failed for {payment.user.username}: {result['message']}", level='error')
            except Exception as e:
                self.message_user(request, f"Error for {payment.user.username}: {str(e)}", level='error')
    
    initiate_stk_push_action.short_description = "Initiate M-Pesa STK Push"


# ============= EVENT CREW MANAGEMENT ADMIN =============
# ============= EMAIL NOTIFICATION ADMIN =============
@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'is_sent', 'sent_at', 'failed_attempts', 'created_at')
    list_filter = ('notification_type', 'is_sent', 'created_at')
    search_fields = ('recipient', 'subject', 'user__username')
    readonly_fields = ('created_at', 'sent_at', 'last_error')
    
    fieldsets = (
        ('Recipient', {
            'fields': ('recipient', 'user')
        }),
        ('Content', {
            'fields': ('notification_type', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('is_sent', 'sent_at', 'failed_attempts', 'last_error', 'created_at')
        }),
    )
    
    actions = ['resend_notifications']
    
    def resend_notifications(self, request, queryset):
        """Resend failed notifications"""
        from .email_utils import EventCRMNotifier
        
        count = 0
        for notification in queryset.filter(is_sent=False):
            try:
                EventCRMNotifier._queue_email(notification)
                count += 1
            except Exception as e:
                self.message_user(request, f"Error resending to {notification.recipient}: {str(e)}", level='error')
        
        self.message_user(request, f"Resent {count} notifications")
    resend_notifications.short_description = "Resend Failed Notifications"


# Unregister the default User admin if it exists
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Register custom User admin
admin.site.register(User, CustomUserAdmin)

# Rename Employee Onboarding to Employee
from attendance.models import EmployeeOnboarding
EmployeeOnboarding._meta.verbose_name = "Employee"
EmployeeOnboarding._meta.verbose_name_plural = "Employees"