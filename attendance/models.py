from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    disability = models.CharField(max_length=255, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class BalanceAdjustment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='adjustments')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='made_adjustments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.amount >= 0 else "-"
        return f"{self.profile.user.username} {sign}{abs(self.amount)} on {self.date.strftime('%Y-%m-%d')}"


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
    event = models.CharField(max_length=100, blank=True, null=True)
    overtime_hours = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    admin_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    @property
    def daily_pay(self):
        base_pay = 1000
        overtime_rate = 100
        return base_pay + (self.overtime_hours * overtime_rate)

#@receiver(post_save, sender=AttendanceRecord)
#def update_balance_on_attendance(sender, instance, created, **kwargs):
    #if created:
        #profile = Profile.objects.get(user=instance.user)
        #amount = instance.daily_pay
        #profile.balance += amount
        #profile.save()


# Remove the first signal completely

#@receiver(post_save, sender=AttendanceRecord)
#def update_user_balance(sender, instance, **kwargs):
    #profile, created = Profile.objects.get_or_create(user=instance.user)
    
    # Sum the daily_pay of unpaid records, not amount_paid
    #total_unpaid = AttendanceRecord.objects.filter(
        #user=instance.user, is_paid=False
    #).aggregate(total=Sum('daily_pay'))['total'] or 0  # FIXED: daily_pay instead of amount_paid

    #profile.balance = total_unpaid
    #profile.save()



@receiver(post_save, sender=AttendanceRecord)
def update_balance_on_attendance(sender, instance, **kwargs):
    profile = Profile.objects.get(user=instance.user)
    
    # Always recalculate total from all unpaid records
    total_unpaid = AttendanceRecord.objects.filter(
        user=instance.user, 
        is_paid=False
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    profile.balance = total_unpaid
    profile.save()