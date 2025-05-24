from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lab_app.models import UserProfile
from allauth.account.models import EmailAddress
import logging

class Command(BaseCommand):
    help = 'Test the authentication flow by creating a test user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='test@example.com', help='Email for test user')
        parser.add_argument('--password', type=str, default='testpassword', help='Password for test user')
        parser.add_argument('--admin', action='store_true', help='Create as admin user')
        parser.add_argument('--force', action='store_true', help='Force recreation if user exists')

    def handle(self, *args, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        is_admin = kwargs.get('admin')
        force = kwargs.get('force')
        
        try:
            # Check if user already exists
            user = User.objects.get(email=email)
            if force:
                user.delete()
                self.stdout.write(self.style.WARNING(f"Deleted existing user: {email}"))
            else:
                self.stdout.write(self.style.WARNING(f"User already exists: {email}"))
                return
        except User.DoesNotExist:
            pass
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_staff=is_admin,
            is_superuser=is_admin
        )
        
        # Create verified email address
        EmailAddress.objects.create(
            user=user,
            email=email,
            primary=True,
            verified=True
        )
        
        # Create profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'full_name': 'Test User',
                'college_id': 'TEST001',
                'branch': 'CSE',
                'current_semester': 1,
                'contact_number': '1234567890',
                'role': 'admin' if is_admin else 'student',
                'is_profile_complete': True
            }
        )
        
        user_type = "admin" if is_admin else "student"
        self.stdout.write(self.style.SUCCESS(f"Successfully created test {user_type} user: {email}"))
        self.stdout.write(f"Email: {email}")
        self.stdout.write(f"Password: {password}")
        self.stdout.write(f"Profile complete: {profile.is_profile_complete}")
        self.stdout.write("\nYou can now login with these credentials to test the authentication flow.")
