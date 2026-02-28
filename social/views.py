from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Friend, SocialPost, Comment, Like, Challenge, ChallengeParticipant, Leaderboard, LeaderboardEntry
from workouts.models import WorkoutSession
from .serializers import (
    FriendSerializer, SocialPostSerializer, SocialPostCreateSerializer,
    CommentSerializer, CommentCreateSerializer, UserBasicSerializer,
    ChallengeSerializer, ChallengeCreateSerializer,
    LeaderboardSerializer, ChallengeParticipantSerializer
)

User = get_user_model()

class FriendViewSet(viewsets.ModelViewSet):
    """Manage friend relationships"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendSerializer
    
    def get_queryset(self):
        return Friend.objects.filter(
            Q(from_user=self.request.user) | Q(to_user=self.request.user)
        )
    
    @action(detail=False, methods=['post'])
    def follow(self, request):
        """Follow a user"""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_to_follow = get_object_or_404(User, id=user_id)
        
        if request.user == user_to_follow:
            return Response(
                {'error': 'You cannot follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        friend, created = Friend.objects.get_or_create(
            from_user=request.user,
            to_user=user_to_follow
        )
        
        if created:
            # Create notification for the user being followed
            from notifications.models import Notification
            Notification.objects.create(
                recipient=user_to_follow,
                actor=request.user,
                verb='follow',
                target=request.user
            )
            
            return Response({
                'message': f'You are now following {user_to_follow.username}',
                'friend': FriendSerializer(friend).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Already following this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def unfollow(self, request):
        """Unfollow a user"""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_to_unfollow = get_object_or_404(User, id=user_id)
        
        deleted = Friend.objects.filter(
            from_user=request.user,
            to_user=user_to_unfollow
        ).delete()
        
        if deleted[0] > 0:
            return Response({
                'message': f'You have unfollowed {user_to_unfollow.username}'
            })
        else:
            return Response(
                {'error': 'You were not following this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def followers(self, request):
        """Get users who follow me"""
        followers = Friend.objects.filter(to_user=request.user)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def following(self, request):
        """Get users I follow"""
        following = Friend.objects.filter(from_user=request.user)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)

class SocialPostViewSet(viewsets.ModelViewSet):
    """Manage social posts"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = SocialPost.objects.all()
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by post type
        post_type = self.request.query_params.get('type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SocialPostCreateSerializer
        return SocialPostSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a post"""
        post = self.get_object()
        
        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if created:
            post.likes.add(request.user)
            
            # Create notification if not your own post
            if post.user != request.user:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=post.user,
                    actor=request.user,
                    verb='like',
                    target=post
                )
            
            return Response({
                'message': 'Post liked',
                'likes_count': post.likes.count()
            })
        else:
            return Response(
                {'error': 'Already liked this post'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """Unlike a post"""
        post = self.get_object()
        
        deleted = Like.objects.filter(
            post=post,
            user=request.user
        ).delete()
        
        if deleted[0] > 0:
            post.likes.remove(request.user)
            return Response({
                'message': 'Post unliked',
                'likes_count': post.likes.count()
            })
        else:
            return Response(
                {'error': 'You had not liked this post'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get all comments for a post"""
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to a post"""
        post = self.get_object()
        serializer = CommentCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            comment = Comment.objects.create(
                post=post,
                user=request.user,
                content=serializer.validated_data['content']
            )
            
            # Create notification if not your own post
            if post.user != request.user:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=post.user,
                    actor=request.user,
                    verb='comment',
                    target=post
                )
            
            return Response(
                CommentSerializer(comment, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedView(generics.ListAPIView):
    """Get activity feed from users you follow"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SocialPostSerializer
    
    def get_queryset(self):
        # Get users I follow
        following = Friend.objects.filter(
            from_user=self.request.user
        ).values_list('to_user', flat=True)
        
        # Include my own posts
        users = list(following) + [self.request.user.id]
        
        return SocialPost.objects.filter(
            user_id__in=users
        ).order_by('-created_at')

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_users(request):
    """Search for users by username"""
    query = request.query_params.get('q', '')
    if len(query) < 2:
        return Response([])
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]
    
    serializer = UserBasicSerializer(users, many=True)
    return Response(serializer.data)

class ChallengeViewSet(viewsets.ModelViewSet):
    """Manage fitness challenges"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Challenge.objects.all()
        
        # Filter by type
        challenge_type = self.request.query_params.get('type')
        if challenge_type:
            queryset = queryset.filter(challenge_type=challenge_type)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Show active challenges
        active = self.request.query_params.get('active')
        if active == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                start_date__lte=today,
                end_date__gte=today
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ChallengeCreateSerializer
        return ChallengeSerializer
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a challenge"""
        challenge = self.get_object()
        
        # Check if already joined
        if challenge.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'Already joined this challenge'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        participant = ChallengeParticipant.objects.create(
            user=request.user,
            challenge=challenge
        )
        
        challenge.participants.add(request.user)
        
        return Response({
            'message': f'Joined challenge: {challenge.title}',
            'participant': ChallengeParticipantSerializer(participant).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a challenge"""
        challenge = self.get_object()
        
        deleted = ChallengeParticipant.objects.filter(
            user=request.user,
            challenge=challenge
        ).delete()
        
        if deleted[0] > 0:
            challenge.participants.remove(request.user)
            return Response({'message': 'Left challenge'})
        else:
            return Response(
                {'error': 'Not a participant'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update user's progress in challenge"""
        challenge = self.get_object()
        
        try:
            participant = ChallengeParticipant.objects.get(
                user=request.user,
                challenge=challenge
            )
        except ChallengeParticipant.DoesNotExist:
            return Response(
                {'error': 'Not a participant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        value = request.data.get('value')
        if value is None:
            return Response(
                {'error': 'value is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        participant.current_value = value
        if participant.current_value >= challenge.target_value and not participant.completed:
            participant.completed = True
            participant.completed_at = timezone.now()
            
            # Create achievement notification
            from notifications.models import Notification
            Notification.objects.create(
                recipient=request.user,
                actor=request.user,
                verb='achievement',
                target=challenge
            )
        
        participant.save()
        
        return Response(ChallengeParticipantSerializer(participant).data)

class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """View leaderboards"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = LeaderboardSerializer
    
    def get_queryset(self):
        return Leaderboard.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current weekly leaderboard"""
        today = timezone.now().date()
        
        # Get or create weekly leaderboard
        leaderboard, created = Leaderboard.objects.get_or_create(
            period='weekly',
            start_date=today - timedelta(days=today.weekday()),
            defaults={'name': f'Week of {today.strftime("%B %d")}'}
        )
        
        # Update leaderboard entries
        if created or not leaderboard.entries.exists():
            self.update_leaderboard(leaderboard)
        
        serializer = self.get_serializer(leaderboard)
        return Response(serializer.data)
    
    def update_leaderboard(self, leaderboard):
        """Update leaderboard with latest data"""
        from workouts.models import WorkoutSession
        from django.db.models import Sum, F, ExpressionWrapper, FloatField
        
        # Calculate total volume per user
        users = User.objects.filter(is_active=True)
        entries = []
        
        for user in users:
            # Calculate total volume from workout sessions
            total_volume = WorkoutSession.objects.filter(
                user=user,
                date__gte=leaderboard.start_date
            ).aggregate(
                total=Sum('sets__weight_kg')
            )['total'] or 0
            
            if total_volume > 0:
                entries.append({
                    'user': user,
                    'value': int(total_volume)
                })
        
        # Sort and assign ranks
        entries.sort(key=lambda x: x['value'], reverse=True)
        
        # Clear old entries
        leaderboard.entries.all().delete()
        
        # Create new entries
        for rank, entry in enumerate(entries[:50], 1):
            LeaderboardEntry.objects.create(
                leaderboard=leaderboard,
                user=entry['user'],
                value=entry['value'],
                rank=rank
            )
