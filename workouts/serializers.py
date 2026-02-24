from rest_framework import serializers
from .models import Exercise, WorkoutSession, ExerciseSet

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'description', 'muscle_group', 'equipment', 'difficulty', 'image_url', 'api_id']
        read_only_fields = ['id', 'api_id']

class ExerciseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'
        read_only_fields = ['id', 'api_id']

class ExerciseSetSerializer(serializers.ModelSerializer):
    exercise_name = serializers.ReadOnlyField(source='exercise.name')
    
    class Meta:
        model = ExerciseSet
        fields = ['id', 'exercise', 'exercise_name', 'sets', 'reps', 'weight_kg', 'rest_seconds', 'order_index']
        read_only_fields = ['id']

class WorkoutSessionSerializer(serializers.ModelSerializer):
    sets = ExerciseSetSerializer(many=True, read_only=True)
    total_sets = serializers.IntegerField(source='sets.count', read_only=True)
    
    class Meta:
        model = WorkoutSession
        fields = ['id', 'date', 'duration_minutes', 'notes', 'created_at', 'sets', 'total_sets']
        read_only_fields = ['id', 'created_at']
