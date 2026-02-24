from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Max, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import WeightEntry, PersonalRecord
from workouts.models import WorkoutSession, ExerciseSet
from .serializers import (
    WeightEntrySerializer, WeightEntryCreateSerializer,
    PersonalRecordSerializer, PersonalRecordCreateSerializer,
    ProgressDashboardSerializer
)

class WeightEntryViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for weight entries
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WeightEntry.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WeightEntryCreateSerializer
        return WeightEntrySerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the most recent weight entry"""
        latest = self.get_queryset().first()
        if latest:
            serializer = self.get_serializer(latest)
            return Response(serializer.data)
        return Response({'message': 'No weight entries found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """Get weight history for charts"""
        entries = self.get_queryset()[:30]  # Last 30 entries
        data = [
            {
                'date': entry.date,
                'weight': float(entry.weight_kg)
            }
            for entry in entries
        ]
        return Response(data)

class PersonalRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for personal records
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PersonalRecord.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PersonalRecordCreateSerializer
        return PersonalRecordSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_exercise(self, request):
        """Get PRs grouped by exercise"""
        exercise_id = request.query_params.get('exercise')
        if exercise_id:
            prs = self.get_queryset().filter(exercise_id=exercise_id)
        else:
            prs = self.get_queryset()
        
        # Get the best PR for each exercise
        best_prs = {}
        for pr in prs:
            if pr.exercise_id not in best_prs or pr.value > best_prs[pr.exercise_id].value:
                best_prs[pr.exercise_id] = pr
        
        serializer = self.get_serializer(best_prs.values(), many=True)
        return Response(serializer.data)

class DashboardView(generics.GenericAPIView):
    """
    Get dashboard statistics
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProgressDashboardSerializer
    
    def get(self, request):
        user = request.user
        
        # Current weight
        current_weight = WeightEntry.objects.filter(user=user).first()
        current_weight_value = current_weight.weight_kg if current_weight else None
        
        # Weight change (last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        old_weight = WeightEntry.objects.filter(
            user=user,
            date__lte=thirty_days_ago
        ).first()
        
        weight_change = None
        if current_weight and old_weight:
            weight_change = float(current_weight.weight_kg) - float(old_weight.weight_kg)
        
        # Workout stats
        total_workouts = WorkoutSession.objects.filter(user=user).count()
        
        # Total exercises performed
        total_exercises = ExerciseSet.objects.filter(
            workout__user=user
        ).values('exercise').distinct().count()
        
        # Personal records count
        pr_count = PersonalRecord.objects.filter(user=user).count()
        
        # Recent workouts
        recent_workouts = WorkoutSession.objects.filter(user=user)[:5]
        recent_data = []
        for w in recent_workouts:
            sets = w.sets.all()
            total_volume = sum(
                float(s.weight_kg or 0) * s.sets * s.reps 
                for s in sets
            )
            recent_data.append({
                'id': w.id,
                'date': w.date,
                'duration': w.duration_minutes,
                'exercises': sets.values('exercise').distinct().count(),
                'total_sets': sets.count(),
                'total_volume': total_volume
            })
        
        # Weight history for chart
        weight_history = []
        weight_entries = WeightEntry.objects.filter(user=user)[:10]
        for entry in weight_entries:
            weight_history.append({
                'date': entry.date,
                'weight': float(entry.weight_kg)
            })
        
        data = {
            'current_weight': current_weight_value,
            'weight_change': weight_change,
            'total_workouts': total_workouts,
            'total_exercises': total_exercises,
            'personal_records': pr_count,
            'recent_workouts': recent_data,
            'weight_history': weight_history
        }
        
        serializer = self.get_serializer(data)
        return Response(serializer.data)
