import requests
from django.core.management.base import BaseCommand
from workouts.models import Exercise

class Command(BaseCommand):
    help = 'Import exercises from wger API'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting exercise import...'))
        
        # Base URL for wger API
        base_url = "https://wger.de/api/v2/exercise/"
        
        # Parameters for the request
        params = {
            'language': 2,  # English
            'limit': 100,
            'offset': 0
        }
        
        # Difficulty mapping
        difficulty_map = {
            1: 'beginner',
            2: 'beginner',
            3: 'intermediate',
            4: 'advanced',
            5: 'advanced'
        }
        
        total_imported = 0
        
        while True:
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data['results']:
                    break
                
                for item in data['results']:
                    # Extract muscle groups
                    muscle_groups = []
                    if item.get('muscles'):
                        # In a real implementation, you might want to fetch muscle names
                        muscle_groups = [str(m) for m in item['muscles']]
                    
                    # Get equipment
                    equipment = []
                    if item.get('equipment'):
                        equipment = [str(e) for e in item['equipment']]
                    
                    # Create or update exercise
                    exercise, created = Exercise.objects.update_or_create(
                        api_id=item['id'],
                        defaults={
                            'name': item['name'],
                            'description': item.get('description', '') or '',
                            'muscle_group': ', '.join(muscle_groups) if muscle_groups else '',
                            'equipment': ', '.join(equipment) if equipment else '',
                            'difficulty': difficulty_map.get(item.get('difficulty', 1), 'beginner')
                        }
                    )
                    
                    if created:
                        total_imported += 1
                        self.stdout.write(f"  ✓ Imported: {item['name']}")
                
                self.stdout.write(self.style.SUCCESS(f"Page {params['offset']//params['limit'] + 1} complete"))
                
                # Check if there are more pages
                if not data.get('next'):
                    break
                    
                params['offset'] += params['limit']
                
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Error fetching data: {e}"))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing data: {e}"))
                break
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully imported {total_imported} new exercises!"))
        self.stdout.write(self.style.SUCCESS(f"Total exercises in database: {Exercise.objects.count()}"))
