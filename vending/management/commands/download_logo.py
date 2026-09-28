from django.core.management.base import BaseCommand
import requests
import os

class Command(BaseCommand):
    help = 'Downloads the LIFO Technologies logo'

    def handle(self, *args, **kwargs):
        logo_url = 'https://www.lifotechnologies.com/assets/images/logo-light.svg'
        logo_path = 'vending/static/admin/img/logo-light.svg'
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(logo_path), exist_ok=True)
        
        # Download the logo
        response = requests.get(logo_url)
        with open(logo_path, 'wb') as f:
            f.write(response.content)
        
        self.stdout.write(self.style.SUCCESS('Successfully downloaded logo')) 