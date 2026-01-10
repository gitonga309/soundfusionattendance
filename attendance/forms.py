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
            'required': 'required'
        }),
        label='Select Event',
        help_text='Select the event you are attending',
        required=False
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
                'class': 'form-control',
                'required': 'required'
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

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        if amount and amount > 50000:
            raise forms.ValidationError("Amount cannot exceed KSH 50,000.")
        return amount