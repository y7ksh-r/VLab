from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lab_app.models import UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates an admin user and profile'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username')
        parser.add_argument('--email', type=str, help='Admin email')
        parser.add_argument('--password', type=str, help='Admin password')
        parser.add_argument('--full-name', type=str, help='Admin full name')
        parser.add_argument('--college-id', type=str, help='Admin college ID')

    def handle(self, *args, **kwargs):
        username = kwargs.get('username') or input('Enter username: ')
        email = kwargs.get('email') or input('Enter email: ')
        password = kwargs.get('password') or input('Enter password: ')
        full_name = kwargs.get('full_name') or input('Enter full name: ')
        college_id = kwargs.get('college_id') or input('Enter college ID: ')

        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )

                # Update or create profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.role = 'admin'
                profile.full_name = full_name
                profile.college_id = college_id
                profile.branch = 'CSE'  # Default value
                profile.current_semester = 1  # Default value
                profile.contact_number = '9999999999'  # Default value
                profile.is_profile_complete = True
                profile.save()

                self.stdout.write(self.style.SUCCESS(f'Admin user {username} created successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {e}'))
