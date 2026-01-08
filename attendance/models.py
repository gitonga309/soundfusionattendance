from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from django.core.cache import cache



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    disability = models.CharField(max_length=255, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class AttendanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    check_in_time = models.TimeField(default=timezone.now)
    event_fk = models.ForeignKey('Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_records')
    overtime_hours = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    admin_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    overtime_edited = models.BooleanField(default=False)
    original_overtime_hours = models.PositiveIntegerField(default=0)

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
    profile = Profile.objects.get(user=instance.user)
    
    # Recalculate total from all unpaid records
    total_attendance = AttendanceRecord.objects.filter(
        user=instance.user, 
        is_paid=False
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Final balance = attendance payments only
    profile.balance = total_attendance
    profile.save()


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
    """When an expense reimbursement is approved, add it to the user's balance"""
    if instance.status == 'approved' and instance.approved_at:
        # Update user profile balance
        profile = instance.user.profile
        # Recalculate total from all unpaid records + adjustments + approved reimbursements
        total_attendance = AttendanceRecord.objects.filter(
            user=instance.user, 
            is_paid=False
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        total_adjustments = BalanceAdjustment.objects.filter(
            user=instance.user
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_reimbursements = ExpenseReimbursement.objects.filter(
            user=instance.user,
            status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        profile.balance = total_attendance + total_adjustments + total_reimbursements
        profile.save()
