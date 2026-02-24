import requests
from django.core.management.base import BaseCommand
from workouts.models import Exercise

class Command(BaseCommand):
    help = 'Import exercises from wger API with related data'

    def fetch_muscle_names(self):
        """Fetch all muscle names and create a mapping"""
        try:
            response = requests.get("https://wger.de/api/v2/muscle/")
            if response.status_code == 200:
                data = response.json()
                muscle_map = {}
                for muscle in data['results']:
                    muscle_map[muscle['id']] = muscle['name']
                return muscle_map
        except:
            return {}
        return {}

    def fetch_equipment_names(self):
        """Fetch all equipment names and create a mapping"""
        try:
            response = requests.get("https://wger.de/api/v2/equipment/")
            if response.status_code == 200:
                data = response.json()
                equipment_map = {}
                for eq in data['results']:
                    equipment_map[eq['id']] = eq['name']
                return equipment_map
        except:
            return {}
        return {}

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting exercise import...'))
        
        # First fetch all reference data
        muscle_map = self.fetch_muscle_names()
        equipment_map = self.fetch_equipment_names()
        
        # Fetch exercises
        base_url = "https://wger.de/api/v2/exercise/"
        params = {
            'language': 2,  # English
            'limit': 50,
            'offset': 0
        }
        
        # We'll need exercise names from a separate endpoint
        # For now, we'll use the exerciseinfo endpoint which has more data
        info_url = "https://wger.de/api/v2/exerciseinfo/"
        
        total_imported = 0
        
        while True:
            try:
                response = requests.get(info_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = data.get('results', [])
                if not results:
                    break
                
                for item in results:
                    # Get muscle names from IDs
                    muscle_names = []
                    for muscle_id in item.get('muscles', []):
                        if muscle_id in muscle_map:
                            muscle_names.append(muscle_map[muscle_id])
                    
                    # Get equipment names from IDs
                    equipment_names = []
                    for eq_id in item.get('equipment', []):
                        if eq_id in equipment_map:
                            equipment_names.append(equipment_map[eq_id])
                    
                    # Create exercise
                    exercise, created = Exercise.objects.update_or_create(
                        api_id=item.get('id'),
                        defaults={
                            'name': item.get('name', 'Unknown')[:200],
                            'description': item.get('description', '')[:1000],
                            'muscle_group': ', '.join(muscle_names) if muscle_names else '',
                            'equipment': ', '.join(equipment_names) if equipment_names else '',
                            'difficulty': item.get('difficulty', 'beginner')
                        }
                    )
                    
                    if created:
                        total_imported += 1
                        self.stdout.write(f"  ✓ Imported: {item.get('name', 'Unknown')}")
                
                if not data.get('next'):
                    break
                    
                params['offset'] += params['limit']
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
                break
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Imported {total_imported} exercises!"))
