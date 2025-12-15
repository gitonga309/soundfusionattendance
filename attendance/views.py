from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import UserRegisterForm, AttendanceForm, EventForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import AttendanceRecord, Profile, Event, BalanceAdjustment
from django.utils import timezone
from django.db.models import Sum

def home(request):
    """Landing page"""
    return render(request, 'attendance/home.html')

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

    # Fetch today's attendance with select_related for event
    try:
        today_record = AttendanceRecord.objects.select_related('event_fk').get(user=user, date=today)
        attendance_status = "Recorded"
    except AttendanceRecord.DoesNotExist:
        today_record = None
        attendance_status = "Not recorded"

    # Get total balance from Profile
    profile = Profile.objects.get(user=user)
    total_balance = profile.balance

    # Get last 5 attendance records for recent balance changes
    recent_records = AttendanceRecord.objects.filter(user=user).select_related('event_fk').order_by('-date')[:5]
    
    # Get last 5 balance adjustments made by admin
    recent_adjustments = BalanceAdjustment.objects.filter(user=user).order_by('-date')[:5]

    context = {
        'user': user,
        'today_record': today_record,
        'attendance_status': attendance_status,
        'total_balance': total_balance,
        'recent_records': recent_records,
        'recent_adjustments': recent_adjustments,
    }

    return render(request, 'attendance/dashboard.html', context)

@login_required
def view_attendance(request):
    user = request.user
    # Optimize query with select_related for event_fk
    records = AttendanceRecord.objects.filter(user=user).select_related('event_fk').order_by('-date')
    
    # Get total balance from Profile
    profile = Profile.objects.get(user=user)
    total_balance = profile.balance
    
    return render(request, 'attendance/view_attendance.html', {
        'records': records,
        'total_balance': total_balance
    })


@login_required
def mark_attendance(request):
    today = timezone.now().date()
    user = request.user

    # Check if record exists for today - limit to once per day
    try:
        record = AttendanceRecord.objects.get(user=user, date=today)
        messages.warning(request, "You have already marked attendance today. You can edit it in your records if needed.")
        return redirect('view_attendance')
    except AttendanceRecord.DoesNotExist:
        record = AttendanceRecord(user=user, date=today)

    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=record)
        if form.is_valid():
            record = form.save(commit=False)
            
            # Force today's date and current time
            record.date = today
            record.check_in_time = timezone.now().time()
            
            # Calculate amount_paid based on overtime
            record.amount_paid = 1000 + (record.overtime_hours * 100)
            
            # Store original overtime hours on first creation
            record.original_overtime_hours = record.overtime_hours
            
            record.save()
            
            messages.success(request, "Attendance marked successfully!")
            return redirect('dashboard')
    else:
        form = AttendanceForm(instance=record)

    return render(request, 'attendance/mark_attendance.html', {
        'form': form, 
        'record': record,
        'today': today
    })

@login_required
def edit_attendance(request, record_id):
    record = get_object_or_404(AttendanceRecord, pk=record_id, user=request.user)

    # Check if overtime has already been edited
    if record.overtime_edited:
        messages.error(request, "You can only edit overtime once per day. Further changes require admin approval.")
        return redirect('view_attendance')

    if request.method == 'POST':
        # Get new overtime from form
        overtime_hours = request.POST.get('overtime_hours')
        event_id = request.POST.get('event_fk')
        
        try:
            overtime_hours = int(overtime_hours)
        except (ValueError, TypeError):
            messages.error(request, "Overtime must be a valid number")
            return redirect('view_attendance')

        # Store the old amount earned
        old_earned = 1000 + (record.overtime_hours * 100)
        
        # Update record with new overtime and event
        record.overtime_hours = overtime_hours
        if event_id:
            try:
                record.event_fk = Event.objects.get(pk=event_id)
            except Event.DoesNotExist:
                messages.error(request, "Selected event does not exist")
                return redirect('view_attendance')
        
        # Calculate NEW earned amount
        new_earned = 1000 + (overtime_hours * 100)
        
        # Update amount_paid: subtract old earned amount, add new earned amount
        # This accounts for admin adjustments that may have been made
        record.amount_paid = (record.amount_paid - old_earned) + new_earned
        
        record.overtime_edited = True  # Mark as edited
        record.save()
        
        # Balance will be automatically recalculated by signal handler
        # Signal will sum all unpaid records + all adjustments
        
        old_ot = record.original_overtime_hours if hasattr(record, 'original_overtime_hours') else 0
        messages.success(request, f"Attendance updated! Overtime changed from {old_ot}h to {overtime_hours}h. You cannot edit this again today.")
        return redirect('view_attendance')

    events = Event.objects.all().order_by('-date')
    return render(request, 'attendance/edit_attendance.html', {'record': record, 'events': events})

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.filter(is_superuser=False).exclude(username='admin')
    
    if request.method == 'POST':
        for user in users:
            user_id = str(user.id)
            adjustment_amount = request.POST.get(f'adjustment_{user_id}')
            
            if adjustment_amount:
                try:
                    adjustment_amount = float(adjustment_amount)
                    
                    # Create BalanceAdjustment record
                    BalanceAdjustment.objects.create(
                        user=user,
                        adjusted_by=request.user,
                        amount=adjustment_amount,
                        reason=request.POST.get(f'reason_{user_id}', 'Admin adjustment')
                    )
                    
                    # Signal will automatically recalculate balance
                    # Balance = sum of all unpaid attendance + sum of all adjustments
                    
                    messages.success(request, f"Balance adjusted for {user.username}")
                    
                except (ValueError, TypeError):
                    messages.error(request, f"Invalid adjustment amount for {user.username}")
        
        return redirect('admin_dashboard')

    # Get user data with optimized queries
    user_data = []
    users = users.prefetch_related('profile')  # Prefetch profile to avoid N+1 queries
    
    for user in users:
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            profile.balance = 0
            profile.save()
            
        # Use select_related for event_fk to reduce queries
        latest_record = AttendanceRecord.objects.filter(user=user).select_related('event_fk').order_by('-date').first()
        recent_adjustments = BalanceAdjustment.objects.filter(user=user).select_related('adjusted_by').order_by('-date')[:5]
        
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

@user_passes_test(is_admin)
def manage_balances(request):
    """Dedicated view for managing user balances"""
    users = User.objects.filter(is_superuser=False).exclude(username='admin')
    
    if request.method == 'POST':
        for user in users:
            user_id = str(user.id)
            adjustment_amount = request.POST.get(f'adjustment_{user_id}')
            reason = request.POST.get(f'reason_{user_id}', 'Balance adjustment')
            
            if adjustment_amount:
                try:
                    adjustment_amount = float(adjustment_amount)
                    
                    # Create BalanceAdjustment record with correct field names
                    BalanceAdjustment.objects.create(
                        user=user,
                        adjusted_by=request.user,
                        amount=adjustment_amount,
                        reason=reason
                    )
                    
                    # Signal will automatically recalculate balance
                    
                except (ValueError, TypeError):
                    messages.error(request, f"Invalid adjustment amount for {user.username}")
        
        messages.success(request, "All balance adjustments have been saved successfully!")
        return redirect('manage_balances')

    # Prepare user balance data
    user_balance_data = []
    total_balance = 0
    
    for user in users:
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            profile.balance = 0
            profile.save()
        
        user_balance_data.append({
            'user': user,
            'profile': profile,
            'balance': profile.balance,
        })
        total_balance += float(profile.balance)

    context = {
        'user_balance_data': user_balance_data,
        'total_balance': total_balance,
    }
    return render(request, 'attendance/manage_balances.html', context)


@login_required
def user_logout(request):
    """Custom logout view with confirmation"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out successfully!")
        return redirect('login')
    
    return render(request, 'attendance/logout.html')


# ========== EVENT & EQUIPMENT MANAGEMENT ==========

@login_required
@user_passes_test(is_admin)
def events_list(request):
    """List all events"""
    events = Event.objects.select_related('created_by').prefetch_related('equipment_set').order_by('-created_at')
    context = {'events': events}
    return render(request, 'attendance/events_list.html', context)


@login_required
@user_passes_test(is_admin)
def event_create(request):
    """Create a new event"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f"Event '{event.name}' created successfully!")
            return redirect('event_detail', pk=event.id)
    else:
        form = EventForm()
    
    context = {'form': form, 'title': 'Create Event'}
    return render(request, 'attendance/event_form.html', context)


@login_required
@user_passes_test(is_admin)
def event_detail(request, pk):
    """View event details"""
    event = get_object_or_404(Event, pk=pk)
    
    context = {
        'event': event,
    }
    return render(request, 'attendance/event_detail.html', context)


@login_required
@user_passes_test(is_admin)
def event_edit(request, pk):
    """Edit an existing event"""
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event '{event.name}' updated successfully!")
            return redirect('event_detail', pk=event.id)
    else:
        form = EventForm(instance=event)
    
    context = {'form': form, 'event': event, 'title': 'Edit Event'}
    return render(request, 'attendance/event_form.html', context)


@login_required
@user_passes_test(is_admin)
def event_delete(request, pk):
    """Delete an event"""
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        event_name = event.name
        event.delete()
        messages.success(request, f"Event '{event_name}' has been deleted.")
        return redirect('events_list')
    
    context = {'event': event}
    return render(request, 'attendance/event_confirm_delete.html', context)

# Equipment management removed - not fully implemented