from rest_framework import serializers
from .models import WeightEntry, PersonalRecord
from workouts.models import Exercise

class WeightEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightEntry
        fields = ['id', 'weight_kg', 'date', 'notes']
        read_only_fields = ['id']

class WeightEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightEntry
        fields = ['weight_kg', 'date', 'notes']
    
    def validate_weight_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be positive")
        if value > 300:
            raise serializers.ValidationError("Weight seems too high (max 300kg)")
        return value

class PersonalRecordSerializer(serializers.ModelSerializer):
    exercise_name = serializers.ReadOnlyField(source='exercise.name')
    
    class Meta:
        model = PersonalRecord
        fields = ['id', 'exercise', 'exercise_name', 'value', 'date', 'exercise_set']
        read_only_fields = ['id']

class PersonalRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalRecord
        fields = ['exercise', 'value', 'date', 'exercise_set']
    
    def validate_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("PR value must be positive")
        return value

class ProgressDashboardSerializer(serializers.Serializer):
    """Serializer for dashboard stats"""
    current_weight = serializers.DecimalField(max_digits=5, decimal_places=2)
    weight_change = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_workouts = serializers.IntegerField()
    total_exercises = serializers.IntegerField()
    personal_records = serializers.IntegerField()
    recent_workouts = serializers.ListField(child=serializers.DictField())
    weight_history = serializers.ListField(child=serializers.DictField())
