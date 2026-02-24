from django.db import models
from users.models import User

class Exercise(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    muscle_group = models.CharField(max_length=100)
    equipment = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    image_url = models.URLField(blank=True)
    api_id = models.IntegerField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class WorkoutSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    date = models.DateField()
    duration_minutes = models.IntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    class Meta:
        ordering = ['-date']

class ExerciseSet(models.Model):
    workout = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='sets')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField()
    reps = models.IntegerField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    rest_seconds = models.IntegerField(null=True, blank=True)
    order_index = models.IntegerField()
    
    def __str__(self):
        return f"{self.workout} - {self.exercise.name} - {self.sets}x{self.reps}"
    
    class Meta:
        ordering = ['order_index']
