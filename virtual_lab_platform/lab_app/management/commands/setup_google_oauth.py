from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Set up Google OAuth with credentials'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, required=True, help='Google OAuth Client ID')
        parser.add_argument('--client-secret', type=str, required=True, help='Google OAuth Client Secret')
        parser.add_argument('--site-id', type=int, default=1, help='Site ID to associate the OAuth app with')
        parser.add_argument('--site-domain', type=str, help='Update site domain (e.g., localhost:8000 or yourdomain.com)')
        parser.add_argument('--site-name', type=str, help='Update site name (e.g., Development or Production)')

    def handle(self, *args, **kwargs):
        client_id = kwargs.get('client_id')
        client_secret = kwargs.get('client_secret')
        site_id = kwargs.get('site_id')
        site_domain = kwargs.get('site_domain')
        site_name = kwargs.get('site_name')

        # Get or create the site
        try:
            site = Site.objects.get(id=site_id)
            self.stdout.write(f"Found existing site: {site.domain}")
            
            # Update site domain and name if provided
            if site_domain:
                site.domain = site_domain
            if site_name:
                site.name = site_name
            if site_domain or site_name:
                site.save()
                self.stdout.write(self.style.SUCCESS(f"Updated site: {site.domain} ({site.name})"))
        except Site.DoesNotExist:
            site = Site.objects.create(id=site_id, domain=site_domain or 'example.com', name=site_name or 'example')
            self.stdout.write(self.style.SUCCESS(f"Created new site: {site.domain}"))
        
        # Create or update the SocialApp for Google
        google_app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth',
                'client_id': client_id,
                'secret': client_secret,
            }
        )
        
        # Make sure the app is associated with the site
        google_app.sites.add(site)
        
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Google OAuth configuration'))
        else:
            self.stdout.write(self.style.SUCCESS('Successfully updated Google OAuth configuration'))
        
        self.stdout.write(
            self.style.WARNING('\nIMPORTANT: Make sure to add the following URLs to your Google OAuth Authorized Redirect URIs:')
        )
        self.stdout.write(f"    http://{site.domain}/accounts/google/login/callback/")
        self.stdout.write(f"    https://{site.domain}/accounts/google/login/callback/ (if using HTTPS)")