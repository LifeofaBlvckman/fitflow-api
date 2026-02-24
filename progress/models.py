from django.db import models
from users.models import User
from workouts.models import Exercise

class WeightEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weight_entries')
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.weight_kg}kg"
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']

class PersonalRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_records')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='personal_records')
    value = models.DecimalField(max_digits=8, decimal_places=2)  # Could be weight, reps, or time
    date = models.DateField()
    exercise_set = models.ForeignKey('workouts.ExerciseSet', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.name}: {self.value}"
    
    class Meta:
        ordering = ['-value']
        unique_together = ['user', 'exercise', 'value']
