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
            'limit': 50,
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
        page_count = 0
        
        while True:
            try:
                self.stdout.write(f"Fetching page {page_count + 1}...")
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = data.get('results', [])
                if not results:
                    self.stdout.write(self.style.WARNING('No more results found'))
                    break
                
                for item in results:
                    try:
                        # Get the name safely
                        name = item.get('name', '')
                        if not name:
                            continue
                            
                        # Get description
                        description = item.get('description', '') or ''
                        
                        # Get muscle groups
                        muscle_data = item.get('muscles', [])
                        muscle_groups = []
                        for muscle in muscle_data:
                            if isinstance(muscle, dict):
                                muscle_name = muscle.get('name', '')
                            else:
                                # If it's just an ID, we'll need to fetch muscle names separately
                                muscle_groups.append(str(muscle))
                        
                        # Get equipment
                        equipment_data = item.get('equipment', [])
                        equipment = []
                        for eq in equipment_data:
                            if isinstance(eq, dict):
                                eq_name = eq.get('name', '')
                                if eq_name:
                                    equipment.append(eq_name)
                            else:
                                equipment.append(str(eq))
                        
                        # Get difficulty
                        difficulty_value = item.get('difficulty', 1)
                        if isinstance(difficulty_value, dict):
                            difficulty_value = difficulty_value.get('value', 1)
                        
                        # Create or update exercise
                        exercise, created = Exercise.objects.update_or_create(
                            api_id=item.get('id'),
                            defaults={
                                'name': name[:200],  # Truncate to max_length
                                'description': description[:500] if description else '',
                                'muscle_group': ', '.join(muscle_groups) if muscle_groups else '',
                                'equipment': ', '.join(equipment) if equipment else '',
                                'difficulty': difficulty_map.get(int(difficulty_value), 'beginner')
                            }
                        )
                        
                        if created:
                            total_imported += 1
                            self.stdout.write(f"  ✓ Imported: {name[:50]}...")
                        else:
                            self.stdout.write(f"  ↻ Updated: {name[:50]}...")
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  ✗ Error processing exercise: {e}"))
                        continue
                
                page_count += 1
                self.stdout.write(self.style.SUCCESS(f"Page {page_count} complete"))
                
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
