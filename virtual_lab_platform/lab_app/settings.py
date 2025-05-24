"""
App-specific settings for lab_app.
These settings are imported by the main settings.py file.
"""
from django.urls import reverse_lazy

# Django Allauth Settings
ACCOUNT_FORMS = {
    'login': 'lab_app.forms.CustomLoginForm',
    'signup': 'lab_app.forms.CustomSignupForm',
}

# Set account adapter
ACCOUNT_ADAPTER = 'lab_app.adapters.CustomAccountAdapter'

# Authentication pages redirect settings
LOGIN_URL = reverse_lazy('account_login')
LOGIN_REDIRECT_URL = reverse_lazy('lab_app:dashboard')
LOGOUT_REDIRECT_URL = reverse_lazy('lab_app:index')
