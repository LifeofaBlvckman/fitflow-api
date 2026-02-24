import requests
from django.core.management.base import BaseCommand
from workouts.models import Exercise

class Command(BaseCommand):
    help = 'Import exercises from wger API'

    def handle(self, *args, **options):
        url = "https://wger.de/api/v2/exerciseinfo/?language=2&limit=100"
        response = requests.get(url)
        data = response.json()

        count = 0
        for item in data['results']:
            # Get English name from translations
            name = None
            description = ''
            
            # Look for English translation (language=2)
            for translation in item.get('translations', []):
                if translation.get('language') == 2:  # English
                    name = translation.get('name')
                    description = translation.get('description', '')
                    break
            
            if not name:
                name = f"Exercise {item.get('id')}"
            
            # Get muscle groups from muscles array
            muscles = []
            for muscle in item.get('muscles', []):
                if isinstance(muscle, dict):
                    muscle_name = muscle.get('name_en') or muscle.get('name')
                    if muscle_name:
                        muscles.append(muscle_name)
            
            # Get equipment
            equipment = []
            for eq in item.get('equipment', []):
                if isinstance(eq, dict):
                    eq_name = eq.get('name')
                    if eq_name:
                        equipment.append(eq_name)
            
            # Get category
            category = ''
            if isinstance(item.get('category'), dict):
                category = item['category'].get('name', '')
            
            exercise, created = Exercise.objects.update_or_create(
                api_id=item['id'],
                defaults={
                    'name': name[:200],
                    'description': description[:1000] if description else '',
                    'muscle_group': ', '.join(muscles) if muscles else category,
                    'equipment': ', '.join(equipment) if equipment else '',
                    'difficulty': 'intermediate',  # Default
                }
            )
            
            if created:
                count += 1
                self.stdout.write(f"✅ Imported: {name}")
            else:
                self.stdout.write(f"🔄 Updated: {name}")

        self.stdout.write(self.style.SUCCESS(f"\n✨ Imported {count} new exercises!"))
        self.stdout.write(self.style.SUCCESS(f"📊 Total exercises: {Exercise.objects.count()}"))
