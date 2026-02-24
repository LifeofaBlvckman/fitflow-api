import requests
from django.core.management.base import BaseCommand
from workouts.models import Exercise

class Command(BaseCommand):
    help = 'Minimal exercise import'

    def handle(self, *args, **options):
        url = "https://wger.de/api/v2/exerciseinfo/?language=2&limit=100"
        response = requests.get(url)
        data = response.json()
        
        count = 0
        for item in data['results']:
            exercise, created = Exercise.objects.get_or_create(
                api_id=item['id'],
                defaults={
                    'name': item.get('name', 'Unknown')[:200],
                    'description': item.get('description', '')[:500],
                }
            )
            if created:
                count += 1
                self.stdout.write(f"Imported: {item.get('name', 'Unknown')}")
        
        self.stdout.write(self.style.SUCCESS(f"Imported {count} exercises"))
