from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import Exercise, WorkoutSession, ExerciseSet
from .serializers import (
    ExerciseSerializer, ExerciseDetailSerializer,
    WorkoutSessionSerializer, ExerciseSetSerializer
)

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View exercises (read-only)
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'muscle_group']
    filterset_fields = ['muscle_group', 'difficulty', 'equipment']
    
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """
        Get detailed exercise information
        """
        exercise = self.get_object()
        serializer = ExerciseDetailSerializer(exercise)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def muscle_groups(self, request):
        """
        Get all unique muscle groups
        """
        muscle_groups = Exercise.objects.values_list('muscle_group', flat=True).distinct()
        return Response(list(filter(None, muscle_groups)))
    
    @action(detail=False, methods=['get'])
    def equipment(self, request):
        """
        Get all unique equipment
        """
        equipment = Exercise.objects.values_list('equipment', flat=True).distinct()
        return Response(list(filter(None, equipment)))

class WorkoutSessionViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for workout sessions
    """
    serializer_class = WorkoutSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_set(self, request, pk=None):
        """
        Add an exercise set to a workout
        """
        workout = self.get_object()
        serializer = ExerciseSetSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(workout=workout)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """
        Get workouts for calendar view
        """
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        queryset = self.get_queryset()
        if month and year:
            queryset = queryset.filter(date__month=month, date__year=year)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ExerciseSetViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for exercise sets
    """
    serializer_class = ExerciseSetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ExerciseSet.objects.filter(workout__user=self.request.user)
    
    def perform_create(self, serializer):
        # Ensure the workout belongs to the user
        workout_id = self.request.data.get('workout')
        workout = WorkoutSession.objects.get(id=workout_id, user=self.request.user)
        serializer.save(workout=workout)
