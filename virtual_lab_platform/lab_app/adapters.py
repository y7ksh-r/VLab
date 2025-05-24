"""
Custom adapters for django-allauth.
"""
from django.urls import reverse
from allauth.account.adapter import DefaultAccountAdapter
from .models import UserProfile

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter that redirects users to the profile completion page
    if their profile is not complete.
    """
    
    def get_login_redirect_url(self, request):
        """
        Redirect users based on their profile completion status.
        """
        user = request.user
        
        # Check if the user profile is complete
        try:
            profile = user.profile
            if not profile.is_profile_complete:
                return reverse('lab_app:complete_profile')
            else:
                # Profile is complete, redirect to dashboard
                return reverse('lab_app:dashboard')
        except UserProfile.DoesNotExist:
            # Create a profile and redirect to complete it
            UserProfile.objects.create(
                user=user,
                branch='CSE',  # Explicitly set default values
                current_semester=1
            )
            return reverse('lab_app:complete_profile')
    
    def get_signup_redirect_url(self, request):
        """
        Redirect newly signed-up users to the profile completion page.
        """
        return reverse('lab_app:complete_profile')
