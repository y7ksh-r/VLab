from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_updated, social_account_added
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(
            user=instance,
            branch='CSE',  # Explicitly set default values
            current_semester=1
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(
            user=instance,
            branch='CSE',  # Explicitly set default values
            current_semester=1
        )

@receiver(user_signed_up)
def handle_user_signed_up(request, user, **kwargs):
    """Handle creation of profile when a user signs up via any method."""
    # Check if the user already has a profile
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=user,
            branch='CSE',  # Explicitly set default values
            current_semester=1
        )
    
    # If user signed up via social account, populate profile with social data
    sociallogin = kwargs.get('sociallogin')
    if sociallogin:
        update_profile_from_social_account(user, sociallogin)

@receiver(social_account_added)
@receiver(social_account_updated)
def update_profile_from_social_account_signal(request, sociallogin, **kwargs):
    """Update profile when a social account is added or updated."""
    update_profile_from_social_account(sociallogin.user, sociallogin)

def update_profile_from_social_account(user, sociallogin):
    """Update user profile with data from social account."""
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=user,
            branch='CSE',  # Explicitly set default values
            current_semester=1
        )

    account = sociallogin.account
    extra_data = account.extra_data
    
    # Handle Google provider
    if account.provider == 'google':
        # Only update fields that are empty
        if not profile.full_name and 'name' in extra_data:
            profile.full_name = extra_data.get('name', '')
        
        # Use email as temporary college ID if not set
        if not profile.college_id and user.email:
            email_username = user.email.split('@')[0]
            profile.college_id = f"TEMP_{email_username[:10]}"
              # Set default values if not set
        if not profile.branch:
            profile.branch = 'CSE'  # Default branch
            
        if not profile.current_semester:
            profile.current_semester = 1  # Default semester
            
        if not profile.contact_number:
            profile.contact_number = '0000000000'  # Default contact number
            
        profile.save()

@receiver(post_save, sender=UserProfile)
def update_user_staff_status(sender, instance, **kwargs):
    """Update user's is_staff status based on their role in the profile."""
    user = instance.user
    
    # If profile role is admin, make sure user has staff status
    if instance.role == 'admin' and not user.is_staff:
        user.is_staff = True
        user.save(update_fields=['is_staff'])
    
    # If profile role is not admin but user has staff status, remove it
    elif instance.role != 'admin' and user.is_staff and not user.is_superuser:
        user.is_staff = False
        user.save(update_fields=['is_staff'])
