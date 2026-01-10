from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import UserRegisterForm, AttendanceForm, EventForm, ExpenseReimbursementForm, EmploymentTypeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import AttendanceRecord, Profile, Event, BalanceAdjustment, ExpenseReimbursement, EmployeeOnboarding
from django.utils import timezone
from django.db.models import Sum

def home(request):
    """Landing page"""
    return render(request, 'attendance/home.html')

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
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            
            # Get or create Profile (signal also creates it, so use get_or_create)
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': form.cleaned_data.get('phone_number'),
                    'email': form.cleaned_data.get('email'),
                    'date_of_birth': form.cleaned_data.get('date_of_birth'),
                    'disability': form.cleaned_data.get('disability'),
                    'employment_type': employment_type
                }
            )
            
            # Update if it was created by signal
            if not created:
                profile.phone_number = form.cleaned_data.get('phone_number')
                profile.email = form.cleaned_data.get('email')
                profile.date_of_birth = form.cleaned_data.get('date_of_birth')
                profile.disability = form.cleaned_data.get('disability')
                profile.employment_type = employment_type
                profile.save()
            
            # If salaried, redirect to onboarding
            if employment_type == 'salaried':
                # Create pending onboarding record
                EmployeeOnboarding.objects.create(
                    user=user,
                    first_name=user.first_name or user.username,
                    last_name=user.last_name or '',
                    email=user.email,
                    phone_number=profile.phone_number,
                    status='pending'
                )
                messages.success(request, "Account created! Please fill in your employment details.")
                return redirect('complete_onboarding')
            else:
                # Casual laborer - direct to dashboard
                messages.success(request, "Account created successfully! Please log in.")
                # Clear session
                if 'employment_type' in request.session:
                    del request.session['employment_type']
                return redirect('login')
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form,
        'employment_type': employment_type,
        'employment_type_display': dict(EmploymentTypeForm.EMPLOYMENT_CHOICES).get(employment_type)
    }
    return render(request, 'attendance/register.html', context)

@login_required
def complete_onboarding(request):
    """Complete salaried employee onboarding"""
    try:
        onboarding = EmployeeOnboarding.objects.get(user=request.user)
    except EmployeeOnboarding.DoesNotExist:
        messages.warning(request, "No onboarding application found.")
        return redirect('dashboard')
    
    # Check if already completed
    if onboarding.status == 'completed':
        messages.info(request, "Your onboarding has already been approved!")
        return redirect('dashboard')
    elif onboarding.status == 'rejected':
        messages.error(request, f"Your application was rejected: {onboarding.rejection_reason}")
        return redirect('dashboard')
    
    if request.method == 'POST':
        onboarding.first_name = request.POST.get('first_name', onboarding.first_name)
        onboarding.last_name = request.POST.get('last_name', onboarding.last_name)
        onboarding.job_role = request.POST.get('job_role')
        onboarding.monthly_salary = request.POST.get('monthly_salary')
        onboarding.date_of_birth = request.POST.get('date_of_birth') or onboarding.date_of_birth
        onboarding.national_id = request.POST.get('national_id')
        onboarding.bank_account = request.POST.get('bank_account')
        
        # Handle file uploads
        if 'id_photo' in request.FILES:
            onboarding.id_photo = request.FILES['id_photo']
        if 'bank_details' in request.FILES:
            onboarding.bank_details = request.FILES['bank_details']
        
        onboarding.status = 'in_progress'
        onboarding.save()
        
        messages.success(request, "Application submitted! We will review it and get back to you shortly.")
        return redirect('onboarding_status')
    
    return render(request, 'attendance/complete_onboarding.html', {'onboarding': onboarding})

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
    profile = Profile.objects.get(user=user)

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
    
    return render(request, 'attendance/view_attendance.html', {
        'records': records,
        'adjustments': adjustments,
        'total_balance': total_balance
    })


@login_required
def mark_attendance(request):
    today = timezone.now().date()
    user = request.user
    profile = user.profile

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
            
            # Force today's date and capture current time correctly using django timezone
            record.date = today
            # Get current time with timezone awareness
            current_time = timezone.now()
            record.check_in_time = current_time.time()
            
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
        event_id = request.POST.get('event_fk')
        
        try:
            overtime_hours = int(overtime_hours)
        except (ValueError, TypeError):
            messages.error(request, "Overtime must be a valid number")
            return redirect('view_attendance')

        # Store the old amount earned based on employment type
        employment_type = request.user.profile.employment_type
        if employment_type == 'salaried':
            old_earned = record.overtime_hours * 100
        else:
            old_earned = 1000 + (record.overtime_hours * 100)
        
        # Update record with new overtime and event
        record.overtime_hours = overtime_hours
        if event_id:
            try:
                record.event_fk = Event.objects.get(pk=event_id)
            except Event.DoesNotExist:
                messages.error(request, "Selected event does not exist")
                return redirect('view_attendance')
        
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
def admin_reimbursements(request):
    """Admin dashboard to review and approve/reject reimbursements"""
    # Get pending reimbursements
    pending_reimbursements = ExpenseReimbursement.objects.filter(status='pending').select_related('user', 'event').order_by('-requested_at')
    approved_reimbursements = ExpenseReimbursement.objects.filter(status='approved').select_related('user', 'event').order_by('-approved_at')
    rejected_reimbursements = ExpenseReimbursement.objects.filter(status='rejected').select_related('user', 'event').order_by('-requested_at')
    
    context = {
        'pending_reimbursements': pending_reimbursements,
        'approved_reimbursements': approved_reimbursements,
        'rejected_reimbursements': rejected_reimbursements,
        'pending_count': pending_reimbursements.count(),
        'approved_count': approved_reimbursements.count(),
        'rejected_count': rejected_reimbursements.count(),
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
