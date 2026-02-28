from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.SocialPostViewSet, basename='post')
router.register(r'friends', views.FriendViewSet, basename='friend')

urlpatterns = [
    path('', include(router.urls)),
    path('feed/', views.FeedView.as_view(), name='social-feed'),
    path('search/', views.search_users, name='user-search'),
]
