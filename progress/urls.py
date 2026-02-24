from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'weight', views.WeightEntryViewSet, basename='weight')
router.register(r'prs', views.PersonalRecordViewSet, basename='pr')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
