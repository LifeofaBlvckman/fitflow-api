from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'exercises', views.ExerciseViewSet, basename='exercise')
router.register(r'workouts', views.WorkoutSessionViewSet, basename='workout')
router.register(r'sets', views.ExerciseSetViewSet, basename='set')

urlpatterns = [
    path('', include(router.urls)),
]
