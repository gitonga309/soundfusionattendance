# attendance/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile
from .models import AttendanceRecord

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

    # Validate email uniqueness
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    # Validate username uniqueness
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    # Validate phone number uniqueness
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("This phone number is already registered.")
        return phone_number

    # Ensure passwords match
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    # Save user and profile
    def save(self, commit=True):
        user = super().save(commit=False)  # Don't commit yet
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'phone_number': self.cleaned_data.get('phone_number'),
                    'date_of_birth': self.cleaned_data.get('date_of_birth'),
                    'disability': self.cleaned_data.get('disability'),
                    'email': self.cleaned_data.get('email'),  # keep in Profile if you want
                }
            )
        return user
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['event', 'overtime_hours', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        overtime = cleaned_data.get('overtime_hours', 0)
        if overtime < 0:
            raise forms.ValidationError("Overtime hours cannot be negative.")
        return cleaned_data