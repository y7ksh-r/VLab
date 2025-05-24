from django.utils import timezone
from datetime import timedelta

def get_session_settings():
    """Get session settings for diagnostics"""
    from django.conf import settings
    
    return {
        'session_cookie_age': settings.SESSION_COOKIE_AGE,
        'session_expire_at_browser_close': settings.SESSION_EXPIRE_AT_BROWSER_CLOSE,
        'session_save_every_request': settings.SESSION_SAVE_EVERY_REQUEST,
    }

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
