from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from crispy_forms.bootstrap import PrependedText
from .models import UserProfile, Subject, Experiment
from allauth.account.forms import SignupForm, LoginForm
from .utils import add_tailwind_form_styles

class UserProfileForm(forms.ModelForm):
    """Form for creating/updating user profile"""
    
    class Meta:
        model = UserProfile
        fields = ['full_name', 'roll_no', 'branch', 'current_semester', 'division', 'contact_number', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'roll_no': forms.TextInput(attrs={'placeholder': 'Enter your roll number (e.g., 21CS001)'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Enter your contact number'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'space-y-6'
        self.helper.layout = Layout(
            Row(
                Column('full_name', css_class='space-y-2 w-full md:w-1/2 px-2'),
                Column('roll_no', css_class='space-y-2 w-full md:w-1/2 px-2'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('branch', css_class='space-y-2 w-full md:w-1/3 px-2'),
                Column('current_semester', css_class='space-y-2 w-full md:w-1/3 px-2'),
                Column('division', css_class='space-y-2 w-full md:w-1/3 px-2'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('contact_number', css_class='space-y-2 w-full md:w-1/2 px-2'),
                Column('profile_picture', css_class='space-y-2 w-full md:w-1/2 px-2'),
                css_class='flex flex-wrap -mx-2'
            ),
            Submit('submit', 'Complete Profile', css_class='w-full py-3 px-4 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-sm font-medium rounded-md shadow focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 mt-6')
        )
        
        # Add Tailwind CSS classes for styling
        for field_name, field in self.fields.items():
            if field_name == 'profile_picture':
                field.widget.attrs['class'] = 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            else:
                field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'


class EditProfileForm(forms.ModelForm):
    """Form for editing limited profile fields - ONLY name and contact number"""
    
    class Meta:
        model = UserProfile
        fields = ['full_name', 'contact_number', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Enter your contact number'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Explicitly exclude all other fields to prevent any accidental inclusion
        excluded_fields = ['roll_no', 'branch', 'current_semester', 'division', 'role', 'date_joined']
        for field_name in excluded_fields:
            if field_name in self.fields:
                del self.fields[field_name]
        
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'space-y-6'
        self.helper.layout = Layout(
            Row(
                Column('full_name', css_class='space-y-2 w-full px-2'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('contact_number', css_class='space-y-2 w-full md:w-1/2 px-2'),
                Column('profile_picture', css_class='space-y-2 w-full md:w-1/2 px-2'),
                css_class='flex flex-wrap -mx-2'
            ),
            Submit('submit', 'Update Profile', css_class='w-full py-3 px-4 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-sm font-medium rounded-md shadow focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 mt-6')
        )
        
        # Add Tailwind CSS classes for styling
        for field_name, field in self.fields.items():
            if field_name == 'profile_picture':
                field.widget.attrs['class'] = 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            else:
                field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'

from allauth.account.forms import SignupForm, LoginForm

class CustomSignupForm(SignupForm):
    """Custom signup form that integrates with allauth"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove crispy forms helper to avoid conflicts with custom CSS
        self.helper = None
        
        # Remove all widget classes to prevent conflicts with template styling
        for field_name, field in self.fields.items():
            field.widget.attrs.pop('class', None)  # Remove any existing classes
            # Only add minimal necessary attributes
            if field_name == 'email':
                field.widget.attrs['placeholder'] = 'Enter your email address'
                field.widget.attrs['type'] = 'email'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Create a password'
                field.widget.attrs['type'] = 'password'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Confirm your password'
                field.widget.attrs['type'] = 'password'

    def save(self, request):
        # This method is called by allauth
        user = super().save(request)
        # No need to call setup_user_email as the parent SignupForm already does this
        return user
        
        
class CustomLoginForm(LoginForm):
    """Custom login form that integrates with allauth"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove crispy forms helper to avoid conflicts with custom CSS
        self.helper = None
        
        # Remove all widget classes to prevent conflicts with template styling
        for field_name, field in self.fields.items():
            field.widget.attrs.pop('class', None)  # Remove any existing classes
            # Only add minimal necessary attributes
            if field_name == 'login':
                field.widget.attrs['placeholder'] = 'Enter your email address'
                field.widget.attrs['type'] = 'email'
            elif field_name == 'password':
                field.widget.attrs['placeholder'] = 'Enter your password'
                field.widget.attrs['type'] = 'password'
            elif field_name == 'remember':
                field.widget.attrs['type'] = 'checkbox'

# Only keep the necessary forms for user authentication and profile management
