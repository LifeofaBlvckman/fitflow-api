from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    starting_weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fitness_goal = models.TextField(blank=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        ordering = ['-date_joined']
