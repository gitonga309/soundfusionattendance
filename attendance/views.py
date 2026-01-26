from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import UserRegisterForm, AttendanceForm, EventForm, ExpenseReimbursementForm, EmploymentTypeForm, SalariedEmployeeRegistrationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import AttendanceRecord, Profile, Event, BalanceAdjustment, ExpenseReimbursement, EmployeeOnboarding
from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import datetime

def home(request):
    """Landing page"""
    return render(request, 'attendance/home.html')

@require_http_methods(["GET"])
def get_events(request):
    """API endpoint to fetch all events as JSON for autocomplete"""
    events = Event.objects.all().order_by('-date').values('id', 'name', 'date')
    events_list = list(events)
    return JsonResponse({'events': events_list})

def employment_type_selection(request):
    """First step: Choose employment type"""
    if request.method == 'POST':
        form = EmploymentTypeForm(request.POST)
        if form.is_valid():
            employment_type = form.cleaned_data['employment_type']
            request.session['employment_type'] = employment_type
            return redirect('register')
    else:
        form = EmploymentTypeForm()
    
    return render(request, 'attendance/employment_type.html', {'form': form})

def register(request):
    """Second step: Register account"""
    # Check if employment type was selected
    employment_type = request.session.get('employment_type')
    if not employment_type:
        return redirect('employment_type_selection')
    
    # Use appropriate form based on employment type
    FormClass = SalariedEmployeeRegistrationForm if employment_type == 'salaried' else UserRegisterForm
    
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            
            # Get or create Profile
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': form.cleaned_data.get('phone_number'),
                    'email': form.cleaned_data.get('email'),
                    'employment_type': employment_type,
                    'date_of_birth': form.cleaned_data.get('date_of_birth') if employment_type == 'salaried' else None,
                }
            )
            
            # Update if it was created by signal
            if not created:
                profile.phone_number = form.cleaned_data.get('phone_number')
                profile.email = form.cleaned_data.get('email')
                profile.employment_type = employment_type
                if employment_type == 'salaried':
                    profile.date_of_birth = form.cleaned_data.get('date_of_birth')
                    profile.job_role = form.cleaned_data.get('job_role')
                    profile.monthly_salary = form.cleaned_data.get('monthly_salary')
                profile.save()
            else:
                # Update salaried fields if applicable
                if employment_type == 'salaried':
                    profile.job_role = form.cleaned_data.get('job_role')
                    profile.monthly_salary = form.cleaned_data.get('monthly_salary')
                    profile.save()
            
            # If salaried, create onboarding record with all details
            if employment_type == 'salaried':
                onboarding = EmployeeOnboarding.objects.create(
                    user=user,
                    first_name=form.cleaned_data.get('first_name'),
                    last_name=form.cleaned_data.get('last_name'),
                    email=user.email,
                    phone_number=profile.phone_number,
                    job_role=form.cleaned_data.get('job_role'),
                    monthly_salary=form.cleaned_data.get('monthly_salary'),
                    date_of_birth=form.cleaned_data.get('date_of_birth'),
                    national_id=form.cleaned_data.get('national_id'),
                    bank_account=form.cleaned_data.get('bank_account'),
                    id_photo=request.FILES.get('id_photo'),
                    bank_details=request.FILES.get('bank_details'),
                    status='pending'
                )
                messages.success(request, "Account created successfully! Your employment details are pending admin approval. You will be notified once reviewed.")
                # Clear session
                if 'employment_type' in request.session:
                    del request.session['employment_type']
                return redirect('login')
            else:
                # Casual laborer - direct to login
                messages.success(request, "Account created successfully! Please log in.")
                # Clear session
                if 'employment_type' in request.session:
                    del request.session['employment_type']
                return redirect('login')
    else:
        form = FormClass()
    
    context = {
        'form': form,
        'employment_type': employment_type,
        'employment_type_display': dict(EmploymentTypeForm.EMPLOYMENT_CHOICES).get(employment_type)
    }
    return render(request, 'attendance/register.html', context)

@login_required
def complete_onboarding(request):
    """Complete salaried employee onboarding - now employees can self-onboard"""
    try:
        onboarding = EmployeeOnboarding.objects.get(user=request.user)
    except EmployeeOnboarding.DoesNotExist:
        # Create a new onboarding record for the user
        onboarding = EmployeeOnboarding(
            user=request.user,
            first_name=request.user.first_name or request.user.username,
            last_name=request.user.last_name or '',
            email=request.user.email,
            phone_number=request.user.profile.phone_number if hasattr(request.user, 'profile') else '',
            status='pending'
        )
        onboarding.save()
    
    # Don't block if status is completed/rejected, allow re-submission
    if onboarding.status == 'rejected':
        # Allow resubmission after rejection
        pass
    
    from .forms import EmployeeOnboardingForm
    
    if request.method == 'POST':
        form = EmployeeOnboardingForm(request.POST, request.FILES, instance=onboarding)
        if form.is_valid():
            onboarding = form.save(commit=False)
            onboarding.user = request.user
            onboarding.email = request.user.email
            onboarding.status = 'pending'
            onboarding.save()
            
            # Update user's profile with the employment details
            profile = request.user.profile
            profile.job_role = onboarding.job_role
            profile.monthly_salary = onboarding.monthly_salary
            profile.date_of_birth = onboarding.date_of_birth
            profile.save()
            
            messages.success(request, "Your onboarding application has been submitted! We will review it and get back to you shortly.")
            return redirect('onboarding_status')
    else:
        form = EmployeeOnboardingForm(instance=onboarding)
    
    return render(request, 'attendance/complete_onboarding.html', {'form': form, 'onboarding': onboarding})

@login_required
def onboarding_status(request):
    """Check onboarding application status"""
    try:
        onboarding = EmployeeOnboarding.objects.get(user=request.user)
    except EmployeeOnboarding.DoesNotExist:
        return redirect('dashboard')
    
    return render(request, 'attendance/onboarding_status.html', {'onboarding': onboarding})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Validate input
        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'attendance/login.html')
        
        # Check if username exists
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(username=username)
            
            # Check if account is active
            if not user_obj.is_active:
                messages.error(request, "Your account is inactive. Please contact the administrator for assistance.")
                return render(request, 'attendance/login.html')
            
        except User.DoesNotExist:
            messages.error(request, f"Username '{username}' not found. Please check your username and try again or create a new account.")
            return render(request, 'attendance/login.html')
        
        # Try to authenticate
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user is active (redundant but safe)
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Your account is inactive. Please contact the administrator.")
                return render(request, 'attendance/login.html')
        else:
            # Authentication failed - likely wrong password
            messages.error(request, "Incorrect password. Please try again. If you forgot your password, please contact the administrator.")
            return render(request, 'attendance/login.html')

    return render(request, 'attendance/login.html')

@login_required
def dashboard(request):
    from .models import PaymentRecord
    
    user = request.user
    today = timezone.now().date()
    # Use get_or_create to safely get or create profile
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Refresh profile from database to ensure we have latest balance
    profile.refresh_from_db()

    # Fetch today's attendance with select_related for event
    try:
        today_record = AttendanceRecord.objects.select_related('event_fk').get(user=user, date=today)
        attendance_status = "Recorded"
    except AttendanceRecord.DoesNotExist:
        today_record = None
        attendance_status = "Not recorded"

    # Get total balance from Profile
    total_balance = profile.balance

    # Get last 5 attendance records for recent balance changes
    recent_records = AttendanceRecord.objects.filter(user=user).select_related('event_fk').order_by('-date')[:5]
    
    # Get last 5 balance adjustments made by admin
    recent_adjustments = BalanceAdjustment.objects.filter(user=user).order_by('-date')[:5]
    
    # Get last 5 balance adjustments (comprehensive change log)
    balance_changes = recent_adjustments
    
    # Get recent payments marked by user
    payment_records = PaymentRecord.objects.filter(user=user).order_by('-payment_date')[:5]
    
    # Combine and sort all activities by date (most recent first)
    all_activities = []
    
    # Add attendance records
    for record in recent_records:
        # Combine date and check_in_time to create a proper datetime
        record_datetime = datetime.datetime.combine(record.date, record.check_in_time)
        # Make it timezone aware in the app's timezone
        record_datetime = timezone.make_aware(record_datetime, timezone=timezone.get_current_timezone())
        all_activities.append({
            'type': 'attendance',
            'date': record.date,
            'datetime': record_datetime,
            'object': record
        })
    
    # Add balance adjustments
    for adjustment in recent_adjustments:
        all_activities.append({
            'type': 'adjustment',
            'date': adjustment.date,
            'datetime': adjustment.date,
            'object': adjustment
        })
    
    # Add payment records
    for payment in payment_records:
        all_activities.append({
            'type': 'payment',
            'date': payment.payment_date,
            'datetime': payment.payment_date,
            'object': payment
        })
    
    # Sort all activities by datetime, most recent first
    all_activities.sort(key=lambda x: x['datetime'], reverse=True)
    
    # Keep only the top 10 most recent activities
    all_activities = all_activities[:10]

    # For salaried employees, show salary information
    # Check if employee has completed onboarding with status "accepted" or higher
    salary_info = None
    if profile.employment_type == 'salaried':
        # Check onboarding status - show salary once accepted
        try:
            onboarding = EmployeeOnboarding.objects.filter(user=user).latest('submitted_at')
            # Show salary info if status is accepted, completed, or any active status (not pending/rejected)
            if onboarding.status in ['accepted', 'completed']:
                from .models import SalaryPayment
                last_salary = SalaryPayment.objects.filter(user=user).order_by('-month_year').first()
                salary_info = {
                    'job_role': profile.job_role,
                    'monthly_salary': profile.monthly_salary,
                    'last_salary_payment': last_salary,
                    'employment_type': 'Salaried Employee',
                    'onboarding_status': onboarding.get_status_display() if hasattr(onboarding, 'get_status_display') else onboarding.status
                }
        except EmployeeOnboarding.DoesNotExist:
            # No onboarding record, but still salaried - show basic info
            from .models import SalaryPayment
            last_salary = SalaryPayment.objects.filter(user=user).order_by('-month_year').first()
            salary_info = {
                'job_role': profile.job_role,
                'monthly_salary': profile.monthly_salary,
                'last_salary_payment': last_salary,
                'employment_type': 'Salaried Employee'
            }

    context = {
        'user': user,
        'profile': profile,
        'today_record': today_record,
        'attendance_status': attendance_status,
        'total_balance': total_balance,
        'recent_records': recent_records,
        'recent_adjustments': recent_adjustments,
        'balance_changes': balance_changes,
        'payment_records': payment_records,
        'all_activities': all_activities,
        'salary_info': salary_info,
    }

    return render(request, 'attendance/dashboard.html', context)

@login_required
def view_attendance(request):
    user = request.user
    # Optimize query with select_related for event_fk
    records = AttendanceRecord.objects.filter(user=user).select_related('event_fk').order_by('-date')
    
    # Get balance adjustments made by admin - with error handling
    try:
        adjustments = BalanceAdjustment.objects.filter(user=user).select_related('adjusted_by').order_by('-date')
    except Exception as e:
        adjustments = []
        messages.warning(request, "Could not load adjustment history.")
    
    # Get total balance from Profile - ensure it exists
    profile, created = Profile.objects.get_or_create(user=user)
    total_balance = profile.balance
    
    # Get salary info and payment history for salaried employees
    salary_payments = []
    monthly_salary = None
    if profile.employment_type == 'salaried':
        from .models import SalaryPayment
        monthly_salary = profile.monthly_salary
        salary_payments = SalaryPayment.objects.filter(user=user).order_by('-month_year')
    
    return render(request, 'attendance/view_attendance.html', {
        'records': records,
        'adjustments': adjustments,
        'total_balance': total_balance,
        'salary_payments': salary_payments,
        'monthly_salary': monthly_salary,
        'is_salaried': profile.employment_type == 'salaried'
    })


@login_required
def mark_attendance(request):
    today = timezone.now().date()
    user = request.user
    try:
        profile = user.profile
    except AttributeError:
        profile = Profile.objects.create(user=user)

    # Check if record exists for today - limit to once per day
    try:
        record = AttendanceRecord.objects.get(user=user, date=today)
        messages.warning(request, "You have already marked attendance today. You can edit it in your records if needed.")
        return redirect('view_attendance')
    except AttendanceRecord.DoesNotExist:
        record = AttendanceRecord(user=user, date=today)

    if request.method == "POST":
        # Handle event selection - either from dropdown or custom name
        event_fk_input = request.POST.get('event_fk', '').strip()
        event_name_input = request.POST.get('event_name', '').strip()
        
        # Validate and set event
        if event_name_input:
            # User typed a custom event name
            event, _ = Event.objects.get_or_create(
                name=event_name_input,
                date=today,
                defaults={'location': 'Custom Event', 'description': 'User-entered event'}
            )
            record.event_fk = event
        elif event_fk_input:
            # User selected from dropdown
            try:
                record.event_fk = Event.objects.get(pk=int(event_fk_input))
            except (Event.DoesNotExist, ValueError):
                messages.error(request, "Invalid event selected")
                return render(request, 'attendance/mark_attendance.html', {
                    'form': AttendanceForm(instance=record), 
                    'record': record,
                    'today': today
                })
        else:
            messages.error(request, "Please select or type an event name")
            return render(request, 'attendance/mark_attendance.html', {
                'form': AttendanceForm(instance=record), 
                'record': record,
                'today': today
            })
        
        # Validate overtime_hours
        try:
            overtime_hours = int(request.POST.get('overtime_hours', 0))
            if overtime_hours < 0:
                messages.error(request, "Overtime hours cannot be negative")
                return render(request, 'attendance/mark_attendance.html', {
                    'form': AttendanceForm(instance=record), 
                    'record': record,
                    'today': today
                })
        except (ValueError, TypeError):
            messages.error(request, "Overtime hours must be a valid number")
            return render(request, 'attendance/mark_attendance.html', {
                'form': AttendanceForm(instance=record), 
                'record': record,
                'today': today
            })
        
        # All validation passed, save the record
        record.overtime_hours = overtime_hours
            
        # Force today's date and capture current time correctly using django timezone
        record.date = today
        # Get current time with timezone awareness and convert to local timezone
        current_time_aware = timezone.now()
        # Convert to the configured timezone to ensure correct time
        current_time_local = current_time_aware.astimezone(timezone.get_current_timezone())
        record.check_in_time = current_time_local.time()
        
        # Calculate amount_paid based on employment type
        # Salaried: Only overtime (no 1000 KSH base)
        # Hourly: Base 1000 KSH + overtime
        if profile.employment_type == 'salaried':
            # Salaried: Only overtime amount
            record.amount_paid = record.overtime_hours * 100
        else:
            # Hourly: Base + overtime
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
        event_fk_input = request.POST.get('event_fk', '').strip()
        event_name_input = request.POST.get('event_name', '').strip()
        
        try:
            overtime_hours = int(overtime_hours)
        except (ValueError, TypeError):
            messages.error(request, "Overtime must be a valid number")
            return redirect('view_attendance')
        
        # Validate and set event
        if event_name_input:
            # User typed a custom event name
            event, _ = Event.objects.get_or_create(
                name=event_name_input,
                date=record.date,
                defaults={'location': 'Custom Event', 'description': 'User-entered event'}
            )
            record.event_fk = event
        elif event_fk_input:
            # User selected from dropdown
            try:
                record.event_fk = Event.objects.get(pk=int(event_fk_input))
            except (Event.DoesNotExist, ValueError):
                messages.error(request, "Invalid event selected")
                return redirect('view_attendance')
        else:
            messages.error(request, "Please select or type an event name")
            return redirect('view_attendance')

        # Store the old amount earned based on employment type
        try:
            employment_type = request.user.profile.employment_type
        except AttributeError:
            # Profile doesn't exist, create it
            profile, _ = Profile.objects.get_or_create(user=request.user)
            employment_type = profile.employment_type
        if employment_type == 'salaried':
            old_earned = record.overtime_hours * 100
        else:
            old_earned = 1000 + (record.overtime_hours * 100)
        
        # Update record with new overtime
        record.overtime_hours = overtime_hours
        
        # Calculate NEW earned amount based on employment type
        if employment_type == 'salaried':
            new_earned = overtime_hours * 100
        else:
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


@login_required
def my_assignments(request):
    """Show events the current user is assigned to (setup crew or event crew)"""
    user = request.user
    
    # Get events where user is in setup_crew
    setup_assignments = Event.objects.filter(setup_crew=user).order_by('setup_date')
    
    # Get events where user is in event_crew
    event_assignments = Event.objects.filter(event_crew=user).order_by('date')
    
    context = {
        'setup_assignments': setup_assignments,
        'event_assignments': event_assignments,
        'setup_count': setup_assignments.count(),
        'event_count': event_assignments.count(),
        'all_count': setup_assignments.count() + event_assignments.count(),
    }
    
    return render(request, 'attendance/my_assignments.html', context)


# ========== EVENT & EQUIPMENT MANAGEMENT ==========

@login_required
def events_list(request):
    """List all events for today - accessible to all logged-in users"""
    today = timezone.now().date()
    events = Event.objects.filter(date=today).select_related('created_by').order_by('-date')
    context = {
        'events': events,
        'date': today
    }
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
def event_detail(request, pk):
    """View event details - accessible to all logged-in users"""
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


# ========== EXPENSE REIMBURSEMENT ==========

@login_required
def submit_reimbursement(request):
    """Allow users to submit expense reimbursement requests"""
    if request.method == 'POST':
        form = ExpenseReimbursementForm(request.POST, request.FILES)
        if form.is_valid():
            reimbursement = form.save(commit=False)
            reimbursement.user = request.user
            reimbursement.save()
            messages.success(request, "Reimbursement request submitted! Awaiting admin approval.")
            return redirect('view_reimbursements')
    else:
        form = ExpenseReimbursementForm()
    
    context = {'form': form}
    return render(request, 'attendance/submit_reimbursement.html', context)


@login_required
def view_reimbursements(request):
    """Allow users to view their reimbursement requests"""
    user = request.user
    reimbursements = ExpenseReimbursement.objects.filter(user=user).order_by('-requested_at')
    
    context = {
        'reimbursements': reimbursements,
    }
    return render(request, 'attendance/view_reimbursements.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_reimbursements(request):
    """Admin dashboard to review and approve/reject reimbursements"""
    # Handle bulk updates from form submission
    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            changes = data.get('changes', [])
            
            for change in changes:
                try:
                    reimbursement = ExpenseReimbursement.objects.get(pk=change['id'])
                    new_status = change.get('status', reimbursement.status)
                    new_is_paid = change.get('is_paid', reimbursement.is_paid)
                    
                    # Update status if it changed
                    if new_status != reimbursement.status:
                        reimbursement.status = new_status
                        if new_status == 'approved' and not reimbursement.approved_by:
                            reimbursement.approved_by = request.user
                            reimbursement.approved_at = timezone.now()
                        elif new_status == 'rejected' and not reimbursement.rejected_by:
                            reimbursement.rejected_by = request.user
                            reimbursement.rejected_at = timezone.now()
                    
                    # Update paid status if changed
                    if new_is_paid != reimbursement.is_paid:
                        reimbursement.is_paid = new_is_paid
                    
                    reimbursement.save()
                except ExpenseReimbursement.DoesNotExist:
                    pass
            
            return JsonResponse({'success': True, 'message': 'All changes saved successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get all reimbursements ordered by status and date
    all_reimbursements = ExpenseReimbursement.objects.select_related('user', 'event').order_by('-requested_at')
    
    context = {
        'all_reimbursements': all_reimbursements,
    }
    return render(request, 'attendance/admin_reimbursements.html', context)


@login_required
@user_passes_test(is_admin)
def approve_reimbursement(request, reimbursement_id):
    """Approve a reimbursement request"""
    reimbursement = get_object_or_404(ExpenseReimbursement, pk=reimbursement_id)
    
    if request.method == 'POST':
        reimbursement.status = 'approved'
        reimbursement.approved_by = request.user
        reimbursement.approved_at = timezone.now()
        reimbursement.save()
        
        messages.success(request, f"Reimbursement for {reimbursement.user.username} approved! Balance updated.")
        return redirect('admin_reimbursements')
    
    context = {'reimbursement': reimbursement}
    return render(request, 'attendance/reimbursement_action.html', context)


@login_required
@user_passes_test(is_admin)
def reject_reimbursement(request, reimbursement_id):
    """Reject a reimbursement request"""
    reimbursement = get_object_or_404(ExpenseReimbursement, pk=reimbursement_id)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        reimbursement.status = 'rejected'
        reimbursement.rejection_reason = rejection_reason
        reimbursement.save()
        
        messages.success(request, f"Reimbursement for {reimbursement.user.username} rejected.")
        return redirect('admin_reimbursements')
    
    context = {'reimbursement': reimbursement, 'action': 'reject'}
    return render(request, 'attendance/reject_reimbursement.html', context)




@login_required
def mark_payment(request):
    """Mark payment from user balance"""
    from .models import PaymentRecord
    
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method', 'bank_transfer')
        
        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, "Payment amount must be greater than 0.")
                return redirect('dashboard')
            
            if amount > profile.balance:
                messages.error(request, f"Payment amount cannot exceed your current balance of KSH {profile.balance}.")
                return redirect('dashboard')
            
            # Record the payment
            payment = PaymentRecord.objects.create(
                user=user,
                amount=amount,
                payment_method=payment_method
            )
            
            # Update user balance
            old_balance = profile.balance
            profile.balance = float(profile.balance) - amount
            profile.save()
            
            # Refresh from database to confirm save
            profile.refresh_from_db()
            
            # Track balance adjustment
            BalanceAdjustment.objects.create(
                user=user,
                reason=f"Payment marked: {payment_method.replace('_', ' ').title()} - KSH {amount}",
                amount=-amount,
                adjusted_by=user
            )
            
            messages.success(request, f"Payment of KSH {amount} has been marked successfully. Your new balance is KSH {profile.balance}.")
        except (ValueError, TypeError) as e:
            messages.error(request, "Invalid payment amount.")
        
        return redirect('dashboard')
    
    return render(request, 'attendance/mark_payment.html', {'profile': profile})


@login_required
@user_passes_test(is_admin)
def view_user_attendance_history(request, user_id):
    """Admin view to see all attendance records and changes for a specific user"""
    
    target_user = get_object_or_404(User, pk=user_id)
    
    # Get all attendance records for this user
    attendance_records = AttendanceRecord.objects.filter(user=target_user).select_related('event_fk').order_by('-date')
    
    # Get all balance adjustments for this user
    balance_changes = BalanceAdjustment.objects.filter(user=target_user).select_related('adjusted_by').order_by('-date')
    
    # Get profile info
    profile = target_user.profile
    
    context = {
        'target_user': target_user,
        'attendance_records': attendance_records,
        'balance_changes': balance_changes,
        'profile': profile,
    }
    
    return render(request, 'attendance/admin_user_attendance_history.html', context)


@login_required
@user_passes_test(is_admin)
def reimbursement_action(request, reimbursement_id):
    """Handle reimbursement approval/rejection via AJAX or direct request"""
    from django.http import JsonResponse
    
    reimbursement = get_object_or_404(ExpenseReimbursement, pk=reimbursement_id)
    action = request.POST.get('action') or request.GET.get('action')
    
    if not action:
        return JsonResponse({'error': 'No action specified'}, status=400)
    
    if action == 'approve':
        reimbursement.status = 'approved'
        reimbursement.approved_by = request.user
        reimbursement.approved_at = timezone.now()
        reimbursement.save()
        
        # Note: Reimbursements are refunds and do not affect user balance
        message = f"Reimbursement for {reimbursement.user.username} approved!"
        status_msg = "approved"
        
    elif action == 'reject':
        rejection_reason = request.POST.get('rejection_reason', '')
        reimbursement.status = 'rejected'
        reimbursement.rejection_reason = rejection_reason
        reimbursement.save()
        
        message = f"Reimbursement for {reimbursement.user.username} rejected."
        status_msg = "rejected"
    
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'status': status_msg,
            'reimbursement_id': reimbursement_id
        })
    
    messages.success(request, message)
    return redirect('admin_reimbursements')
