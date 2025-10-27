from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import UserRegisterForm, AttendanceForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import AttendanceRecord, Profile, BalanceAdjustment
from django.utils import timezone
from django.db.models import Sum

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'attendance/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'attendance/login.html')

@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    # Fetch today's attendance
    try:
        today_record = AttendanceRecord.objects.get(user=user, date=today)
        attendance_status = "Recorded"
    except AttendanceRecord.DoesNotExist:
        today_record = None
        attendance_status = "Not recorded"

    # Get total balance from Profile (stored in DB)
    profile = Profile.objects.get(user=user)
    total_balance = profile.balance

    # **CORRECTED LINE** - Fetch balance adjustments via profile
    adjustments = BalanceAdjustment.objects.filter(profile=profile).order_by('-date')[:10]

    context = {
        'user': user,
        'today_record': today_record,
        'attendance_status': attendance_status,
        'total_balance': total_balance,
        'adjustments': adjustments,  # This will now work
    }

    return render(request, 'attendance/dashboard.html', context)

@login_required
def view_attendance(request):
    user = request.user
    records = AttendanceRecord.objects.filter(user=user).order_by('-date')
    
    # Get total balance from Profile
    profile = Profile.objects.get(user=user)
    total_balance = profile.balance
    
    return render(request, 'attendance/view_attendance.html', {
        'records': records,
        'total_balance': total_balance  # You were missing this line
    })

@login_required
def mark_attendance(request):
    today = timezone.now().date()
    user = request.user

    # Check if record exists for today
    try:
        record = AttendanceRecord.objects.get(user=user, date=today)
        created = False
    except AttendanceRecord.DoesNotExist:
        record = AttendanceRecord(user=user, date=today)
        created = True

    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            
            # Calculate the NEW amount_paid
            new_amount_paid = 1000 + (record.overtime_hours * 100)
            
            # If UPDATING existing record, adjust balance correctly
            if not created:
                # Get the difference between new and old amount
                old_amount_paid = record.amount_paid  # This gets the OLD value before save
                amount_difference = new_amount_paid - old_amount_paid
            else:
                # If CREATING new record, use full amount
                amount_difference = new_amount_paid
            
            # Set the new amount_paid
            record.amount_paid = new_amount_paid
            record.save()
            
            # Update profile balance with the difference
            profile = Profile.objects.get(user=user)
            profile.balance += amount_difference
            profile.save()
            
            messages.success(request, "Attendance marked successfully!")
            return redirect('dashboard')
    else:
        form = AttendanceForm(instance=record)

    return render(request, 'attendance/mark_attendance.html', {
        'form': form, 
        'record': record,
        'created': created
    })

@login_required
def edit_attendance(request, record_id):
    record = get_object_or_404(AttendanceRecord, pk=record_id, user=request.user)

    if request.method == 'POST':
        # Only allow editing overtime
        overtime_hours = request.POST.get('overtime_hours')
        try:
            overtime_hours = int(overtime_hours)
        except ValueError:
            messages.error(request, "Overtime must be a number")
            return redirect('view_attendance')

        # Get old amount for balance adjustment
        old_amount = record.amount_paid
        
        # Update record
        record.overtime_hours = overtime_hours
        record.amount_paid = 1000 + (overtime_hours * 100)
        record.save()

        # Update profile balance with the difference
        profile = Profile.objects.get(user=request.user)
        profile.balance += (record.amount_paid - old_amount)
        profile.save()
        
        messages.success(request, "Overtime updated successfully!")
        return redirect('view_attendance')

    return render(request, 'attendance/edit_attendance.html', {'record': record})

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all()

    if request.method == 'POST':
        for user in users:
            user_id = str(user.id)
            adjustment_amount = request.POST.get(f'adjustment_{user_id}')
            
            if adjustment_amount:
                try:
                    adjustment_amount = float(adjustment_amount)
                    profile = Profile.objects.get(user=user)
                    
                    # Update profile balance
                    old_balance = profile.balance
                    profile.balance += adjustment_amount
                    profile.save()
                    
                    # Create BalanceAdjustment record
                    BalanceAdjustment.objects.create(
                        profile=profile,
                        admin=request.user,
                        amount=adjustment_amount,
                        reason=request.POST.get(f'reason_{user_id}', 'Admin adjustment')
                    )
                    
                    messages.success(request, f"Balance adjusted for {user.username}: {old_balance} → {profile.balance}")
                    
                except (ValueError, TypeError):
                    messages.error(request, f"Invalid adjustment amount for {user.username}")
        
        return redirect('admin_dashboard')

    # Get user data with their balances from Profile
    user_data = []
    for user in users:
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            profile.balance = 0
            profile.save()
            
        latest_record = AttendanceRecord.objects.filter(user=user).order_by('-date').first()
        recent_adjustments = BalanceAdjustment.objects.filter(profile=profile).order_by('-date')[:5]
        
        user_data.append({
            'user': user,
            'profile': profile,
            'total_balance': profile.balance,
            'latest_record': latest_record,
            'recent_adjustments': recent_adjustments,
        })

    context = {
        'user_data': user_data
    }
    return render(request, 'attendance/admin_dashboard.html', context)