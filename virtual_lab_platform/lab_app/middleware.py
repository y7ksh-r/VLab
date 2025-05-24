from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone

# Define locally to avoid import issues
def extend_session(request):
    """Extend the user's session if needed"""
    if request.user.is_authenticated:
        # Only extend session if close to expiring
        if '_session_init_timestamp_' not in request.session:
            request.session['_session_init_timestamp_'] = timezone.now().timestamp()
        
        # Store last activity time in session
        request.session['_last_activity_'] = timezone.now().timestamp()
        
        # Make sure session info is saved
        request.session.modified = True

class ProfileRequiredMiddleware:
    """
    Middleware to ensure authenticated users have completed their profile
    before accessing lab content
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require profile completion
        self.exempt_paths = [
            '/accounts/',
            '/admin/',
            '/profile/complete/',
            '/static/',
            '/media/',
            '/',  # Home page
            '/about/',
            '/contact/',
        ]
    
    def __call__(self, request):
        # Extend session for authenticated users
        if request.user.is_authenticated:
            extend_session(request)
          # Check if user is authenticated and path requires profile check
        if (request.user.is_authenticated and 
            not self._is_exempt_path(request.path) and
            not request.user.is_superuser and
            not request.user.is_staff):
            
            try:
                profile = request.user.profile
                if not profile.is_profile_complete:
                    messages.warning(
                        request, 
                        'Please complete your profile to access lab content.'
                    )
                    return redirect('lab_app:complete_profile')
            except AttributeError:
                # User doesn't have a profile, redirect to complete profile
                messages.warning(
                    request, 
                    'Please complete your profile to access lab content.'
                )
                return redirect('lab_app:complete_profile')
        
        response = self.get_response(request)
        return response
    
    def _is_exempt_path(self, path):
        """Check if the path is exempt from profile completion requirement"""
        return any(path.startswith(exempt_path) for exempt_path in self.exempt_paths)


class SessionActivityMiddleware:
    """
    Middleware to track user activity and extend session lifetime
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Extend session after processing the request
        if request.user.is_authenticated:
            extend_session(request)
        
        return response
