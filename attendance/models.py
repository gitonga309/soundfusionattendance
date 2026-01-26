from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from django.core.cache import cache



class Profile(models.Model):
    EMPLOYMENT_TYPES = (
        ('casual', 'Casual Laborer'),
        ('salaried', 'Salaried Employee'),
    )
    
    JOB_ROLES = (
        ('repair', 'Repair Technician'),
        ('driver', 'Driver'),
        ('accountant', 'Accountant'),
        ('planner', 'Event Planner'),
        ('cleaner', 'Cleaner'),
        ('other', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    disability = models.CharField(max_length=255, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Employment type and salaried fields
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='casual', 
                                      help_text="Is this person a casual laborer or salaried employee?")
    job_role = models.CharField(max_length=50, choices=JOB_ROLES, blank=True, null=True,
                               help_text="Job role (for salaried employees)")
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True,
                                        help_text="Monthly salary amount (for salaried employees)")

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except AttributeError:
        # Profile might not exist yet, skip
        pass


class AttendanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=lambda: timezone.now().astimezone(timezone.get_current_timezone()).date())
    check_in_time = models.TimeField(default=lambda: timezone.now().astimezone(timezone.get_current_timezone()).time())
    event_fk = models.ForeignKey('Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_records')
    overtime_hours = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Amount")
    admin_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    overtime_edited = models.BooleanField(default=False)
    original_overtime_hours = models.PositiveIntegerField(default=0)
    
    # For salaried employees
    supper_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True,
                                          help_text="Supper allowance for salaried employees")

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    @property
    def daily_pay(self):
        """Calculate daily pay: KSH 1000 base + KSH 100 per overtime hour"""
        base_pay = 1000
        overtime_rate = 100
        return base_pay + (self.overtime_hours * overtime_rate)
    
    @property
    def earned_amount(self):
        """Amount earned from attendance (1000 + 100 per overtime hour)"""
        return 1000 + (self.overtime_hours * 100)


@receiver(post_save, sender=AttendanceRecord)
def update_balance_on_attendance(sender, instance, **kwargs):
    """
    Update user's balance whenever attendance record is created or modified.
    Balance = Sum of all unpaid attendance records
    """
    try:
        profile = Profile.objects.get(user=instance.user)
        
        # Recalculate total from all unpaid records
        total_attendance = AttendanceRecord.objects.filter(
            user=instance.user, 
            is_paid=False
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        # Final balance = attendance payments only
        profile.balance = total_attendance
        profile.save()
    except Profile.DoesNotExist:
        # Profile not created yet, skip
        pass


class Event(models.Model):
    """Model for tracking events and their details"""
    name = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    client_venue = models.CharField(max_length=255, blank=True, help_text="Client venue/location")
    setup_date = models.DateField(null=True, blank=True, help_text="Date when setup starts")
    setup_end_date = models.DateField(null=True, blank=True, help_text="Date when setup is complete / Event ends")
    equipments_delivered = models.TextField(blank=True, help_text="List of equipments delivered to this event")
    
    # User assignments for event work
    setup_crew = models.ManyToManyField(
        User, 
        blank=True, 
        related_name='setup_events',
        help_text="Select users assigned to setup/teardown work"
    )
    event_crew = models.ManyToManyField(
        User, 
        blank=True, 
        related_name='event_day_events',
        help_text="Select users assigned for event day work"
    )
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.date}"

    class Meta:
        ordering = ['-date']


class BalanceAdjustment(models.Model):
    """Track admin adjustments to user balances"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balance_adjustments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True, default="Admin adjustment")
    adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='made_adjustments')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.amount >= 0 else "-"
        return f"{self.user.username} {sign}{abs(self.amount)} on {self.date.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-date']


@receiver(post_save, sender='attendance.BalanceAdjustment')
def update_balance_on_adjustment(sender, instance, **kwargs):
    """Update user's balance when admin makes adjustment"""
    try:
        profile = instance.user.profile
        
        # Recalculate total from all unpaid records
        total_attendance = AttendanceRecord.objects.filter(
            user=instance.user, 
            is_paid=False
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        # Get total from adjustments
        total_adjustments = BalanceAdjustment.objects.filter(
            user=instance.user
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Final balance = attendance payments + adjustments
        profile.balance = total_attendance + total_adjustments
        profile.save()
    except AttributeError:
        # Profile might not exist yet, skip
        pass


class ExpenseReimbursement(models.Model):
    """Model for tracking expense reimbursement requests from users"""
    EXPENSE_TYPES = (
        ('transport', 'Transport (Uber/Bolt)'),
        ('purchase', 'Purchase (Equipment/Supplies)'),
        ('airtime', 'Airtime'),
        ('meal', 'Meal/Food'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_reimbursements')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='reimbursements')
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, help_text="Explain the expense")
    receipt_photo = models.ImageField(upload_to='receipts/', null=True, blank=True, help_text="Upload receipt/proof (optional)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False, verbose_name="Paid")
    
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reimbursements')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection")
    
    def __str__(self):
        return f"{self.user.username} - {self.get_expense_type_display()} - KSH {self.amount} ({self.status})"
    
    class Meta:
        ordering = ['-requested_at']


@receiver(post_save, sender='attendance.ExpenseReimbursement')
def update_balance_on_reimbursement_approval(sender, instance, **kwargs):
    """Reimbursements are refunds and do not affect user balance"""
    # Reimbursements are for refunding money to employees and should not increase their balance
    pass


class SalaryPayment(models.Model):
    """Track monthly salary payments for salaried employees"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salary_payments')
    month_year = models.DateField(help_text="First day of the month for which salary is paid")
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base monthly salary")
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Total overtime pay for the month")
    supper_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Total supper allowance for the month")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount paid (base + overtime + supper)")
    
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_salary_payments')
    paid_at = models.DateTimeField(auto_now_add=True)
    
    notes = models.TextField(blank=True, help_text="Additional notes about this payment")

    def __str__(self):
        return f"{self.user.username} - {self.month_year.strftime('%B %Y')} - KSH {self.total_amount}"

    class Meta:
        ordering = ['-month_year']
        unique_together = ('user', 'month_year')  # Only one payment per user per month


@receiver(post_save, sender='attendance.SalaryPayment')
def update_balance_on_salary_payment(sender, instance, **kwargs):
    """Add salary payment to user's balance"""
    try:
        profile = instance.user.profile
        
        # Recalculate total from all sources
        total_attendance = AttendanceRecord.objects.filter(
            user=instance.user, 
            is_paid=False
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        total_adjustments = BalanceAdjustment.objects.filter(
            user=instance.user
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_salaries = SalaryPayment.objects.filter(
            user=instance.user
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Note: Reimbursements are refunds and should not be included in balance
        profile.balance = total_attendance + total_adjustments + total_salaries
        profile.save()
    except AttributeError:
        # Profile might not exist yet, skip
        pass


# ========== SIGNAL FOR EVENTS MANAGER GROUP ==========
# This signal automatically makes users staff when added to Events Manager group

from django.db.models.signals import m2m_changed
from django.dispatch import receiver as m2m_receiver


@m2m_receiver(m2m_changed, sender=User.groups.through)
def auto_staff_on_events_manager(sender, instance, action, pk_set, **kwargs):
    """
    Automatically enable staff status when a user is added to Events Manager group.
    This makes it seamless to create Events Manager users from admin.
    """
    if action == 'post_add' and pk_set:
        # Get the Events Manager group ID
        try:
            from django.contrib.auth.models import Group
            # Use filter instead of get to avoid exceptions if group doesn't exist
            events_manager_group = Group.objects.filter(name='Events Manager').first()
            
            # If the user was added to Events Manager group, make them staff
            if events_manager_group and events_manager_group.pk in pk_set:
                if not instance.is_staff:
                    instance.is_staff = True
                    instance.save(update_fields=['is_staff'])
        except Exception as e:
            # Silently fail to avoid 500 errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in auto_staff_on_events_manager: {str(e)}")


class EmployeeOnboarding(models.Model):
    """Track salaried employee onboarding process"""
    ONBOARDING_STATUS = [
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    JOB_ROLES = [
        ('repair_technician', 'Repair Technician'),
        ('driver', 'Driver'),
        ('accountant', 'Accountant'),
        ('event_planner', 'Event Planner'),
        ('cleaner', 'Cleaner'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='onboarding', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    job_role = models.CharField(max_length=50, choices=JOB_ROLES, blank=True, null=True)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    national_id = models.CharField(max_length=20, blank=True)
    bank_account = models.CharField(max_length=50, blank=True, help_text="Bank account for salary payments")
    
    # Document uploads
    id_photo = models.FileField(upload_to='onboarding/id_photos/', blank=True)
    employment_letter = models.FileField(upload_to='onboarding/letters/', blank=True)
    bank_details = models.FileField(upload_to='onboarding/bank_details/', blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=ONBOARDING_STATUS, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='onboardings_reviewed')
    rejection_reason = models.TextField(blank=True, help_text="If rejected, provide reason for rejection")
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Onboarding - {self.first_name} {self.last_name} ({self.get_status_display()})"


class PaymentRecord(models.Model):
    """Track when users mark payments/withdrawals from their balance"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=50,
        choices=(
            ('bank_transfer', 'Bank Transfer'),
            ('cash', 'Cash'),
            ('mpesa', 'M-Pesa'),
            ('other', 'Other'),
        ),
        default='bank_transfer'
    )
    reference_number = models.CharField(max_length=100, blank=True, help_text="Transaction/reference number")
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - KSH {self.amount} - {self.payment_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-payment_date']

