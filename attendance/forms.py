from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, AttendanceRecord, Event, ExpenseReimbursement, EmployeeOnboarding

class EmploymentTypeForm(forms.Form):
    """Form to select employment type during signup"""
    EMPLOYMENT_CHOICES = (
        ('casual', 'Casual Laborer - Join us for casual work per event'),
        ('salaried', 'Salaried Employee - Apply for a permanent position'),
    )
    
    employment_type = forms.ChoiceField(
        choices=EMPLOYMENT_CHOICES,
        widget=forms.RadioSelect,
        label='How would you like to join Sound Fusion?',
        help_text='Choose the option that best fits you'
    )

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    disability = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'date_of_birth', 'disability', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("This phone number is already registered.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'phone_number': self.cleaned_data.get('phone_number'),
                    'date_of_birth': self.cleaned_data.get('date_of_birth'),
                    'disability': self.cleaned_data.get('disability'),
                    'email': self.cleaned_data.get('email'),
                }
            )
        return user

class AttendanceForm(forms.ModelForm):
    event_fk = forms.ModelChoiceField(
        queryset=Event.objects.all().order_by('-date'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'list': 'event_list'
        }),
        label='Select or Type Event',
        help_text='Select from existing events or type a new event name',
        required=False
    )
    event_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type event name',
            'autocomplete': 'off'
        }),
        label='Event Name',
        help_text='You can type a custom event name if not found in the list'
    )
    
    class Meta:
        model = AttendanceRecord
        fields = ['event_fk', 'overtime_hours']
        widgets = {
            'overtime_hours': forms.NumberInput(attrs={
                'placeholder': 'Overtime hours',
                'min': '0',
                'value': '0',
                'class': 'form-control'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        overtime = cleaned_data.get('overtime_hours', 0)
        if overtime < 0:
            raise forms.ValidationError("Overtime hours cannot be negative.")
        return cleaned_data


class EventForm(forms.ModelForm):
    """Form for creating and managing events"""
    class Meta:
        model = Event
        fields = ['name', 'date', 'location', 'description', 'client_venue', 'setup_date', 'setup_end_date', 'equipments_delivered']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Event name',
                'class': 'form-control',
                'required': 'required'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Event location/venue',
                'class': 'form-control'
            }),
            'client_venue': forms.TextInput(attrs={
                'placeholder': 'Client venue/location',
                'class': 'form-control'
            }),
            'setup_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'setup_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Event details and notes',
                'class': 'form-control',
                'rows': 4
            }),
            'equipments_delivered': forms.Textarea(attrs={
                'placeholder': 'List of equipments delivered (one per line)',
                'class': 'form-control',
                'rows': 4
            })
        }

class ExpenseReimbursementForm(forms.ModelForm):
    """Form for users to submit expense reimbursement requests"""
    class Meta:
        model = ExpenseReimbursement
        fields = ['event', 'expense_type', 'amount', 'description', 'receipt_photo']
        widgets = {
            'event': forms.Select(attrs={
                'class': 'form-control'
            }),
            'expense_type': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Amount (KSH)',
                'min': '0.01',
                'step': '0.01',
                'class': 'form-control',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Explain what this expense was for (e.g., Uber to event venue)',
                'class': 'form-control',
                'rows': 3
            }),
            'receipt_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make event field optional (not required)
        self.fields['event'].required = False

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        if amount and amount > 50000:
            raise forms.ValidationError("Amount cannot exceed KSH 50,000.")
        return amount


class EmployeeOnboardingForm(forms.ModelForm):
    """Form for salaried employees to complete their onboarding"""
    class Meta:
        model = EmployeeOnboarding
        fields = ['first_name', 'last_name', 'job_role', 'monthly_salary', 'date_of_birth', 'national_id', 'bank_account', 'id_photo', 'bank_details']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
                'required': 'required'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
                'required': 'required'
            }),
            'job_role': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'monthly_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Monthly Salary (KSH)',
                'min': '0',
                'step': '100',
                'required': 'required'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'National ID Number'
            }),
            'bank_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank Account Number'
            }),
            'id_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'bank_details': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
        }
    
    def clean_monthly_salary(self):
        salary = self.cleaned_data.get('monthly_salary')
        if salary and salary <= 0:
            raise forms.ValidationError("Salary must be greater than 0.")
        return salary


class SalariedEmployeeRegistrationForm(UserCreationForm):
    """Combined form for salaried employees to register and complete onboarding in one step"""
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    
    # Onboarding fields
    first_name = forms.CharField(max_length=150, required=True, label="First Name (for employment)")
    last_name = forms.CharField(max_length=150, required=True, label="Last Name (for employment)")
    job_role = forms.ChoiceField(
        choices=Profile.JOB_ROLES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    monthly_salary = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Monthly Salary (KSH)',
            'min': '0',
            'step': '100'
        })
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        label="Date of Birth"
    )
    national_id = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'National ID Number'
        })
    )
    bank_account = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bank Account Number'
        })
    )
    id_photo = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    bank_details = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("This phone number is already registered.")
        return phone_number

    def clean_monthly_salary(self):
        salary = self.cleaned_data.get('monthly_salary')
        if salary and salary <= 0:
            raise ValidationError("Monthly salary must be greater than 0.")
        return salary

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data