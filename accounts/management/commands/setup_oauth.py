from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings
import environ

env = environ.Env()

class Command(BaseCommand):
    help = 'Set up Google OAuth configuration'

    def handle(self, *args, **options):
        # Get domain from environment, default to local development
        domain = env('SITE_DOMAIN', default='127.0.0.1:8000')
        
        # Update the default site
        site = Site.objects.get_current()
        site.domain = domain
        site.name = env('SITE_NAME', default='Todos App')
        site.save()
        self.stdout.write(f'Updated site: {site.domain}')

        # Get credentials from environment
        client_id = env('GOOGLE_OAUTH_CLIENT_ID', default='')
        client_secret = env('GOOGLE_OAUTH_CLIENT_SECRET', default='')

        if not client_id or not client_secret:
            self.stdout.write(
                self.style.WARNING(
                    'Google OAuth credentials not found in environment variables.\n'
                    'Please set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in your .env file.\n'
                    'Get them from: https://console.developers.google.com/'
                )
            )
            return

        # Delete existing Google apps and create a new one to avoid duplicates
        SocialApp.objects.filter(provider='google').delete()
        
        # Create Google Social App
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=client_secret,
        )
        
        google_app.sites.add(site)
        created = True
        
        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(f'{action} Google OAuth app successfully!')
        )
        
        # Determine protocol based on domain
        protocol = 'https' if not domain.startswith('127.0.0.1') and not domain.startswith('localhost') else 'http'
        
        self.stdout.write(
            'Make sure your Google OAuth redirect URI is set to:\n'
            f'{protocol}://{domain}/accounts/google/login/callback/'
        )