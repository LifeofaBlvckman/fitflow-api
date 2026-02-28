from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Friend, SocialPost, Comment, Like, Challenge, ChallengeParticipant, Leaderboard, LeaderboardEntry
from workouts.serializers import WorkoutSessionSerializer

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']

class FriendSerializer(serializers.ModelSerializer):
    from_user = UserBasicSerializer(read_only=True)
    to_user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Friend
        fields = ['id', 'from_user', 'to_user', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user', 'post']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']

class SocialPostSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    workout_details = WorkoutSessionSerializer(source='workout', read_only=True)
    
    class Meta:
        model = SocialPost
        fields = [
            'id', 'user', 'post_type', 'content', 'workout',
            'workout_details', 'likes', 'likes_count', 'comments',
            'comments_count', 'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'likes']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class SocialPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialPost
        fields = ['post_type', 'content', 'workout']
    
    def validate_content(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Content must be at least 2 characters")
        if len(value) > 500:
            raise serializers.ValidationError("Content must be less than 500 characters")
        return value

class ChallengeParticipantSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = ChallengeParticipant
        fields = ['id', 'user', 'current_value', 'progress_percentage', 'joined_at', 'completed']

class ChallengeSerializer(serializers.ModelSerializer):
    creator = UserBasicSerializer(read_only=True)
    participants = ChallengeParticipantSerializer(source='challengeparticipant_set', many=True, read_only=True)
    participants_count = serializers.IntegerField(read_only=True)
    is_participating = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'creator', 'title', 'description', 'challenge_type',
            'difficulty', 'target_value', 'start_date', 'end_date',
            'participants', 'participants_count', 'is_public',
            'is_participating', 'user_progress', 'created_at'
        ]
    
    def get_is_participating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(id=request.user.id).exists()
        return False
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                participant = ChallengeParticipant.objects.get(
                    user=request.user,
                    challenge=obj
                )
                return ChallengeParticipantSerializer(participant).data
            except ChallengeParticipant.DoesNotExist:
                pass
        return None

class ChallengeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            'title', 'description', 'challenge_type',
            'difficulty', 'target_value', 'start_date', 'end_date', 'is_public'
        ]

class LeaderboardEntrySerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = LeaderboardEntry
        fields = ['id', 'user', 'value', 'rank']

class LeaderboardSerializer(serializers.ModelSerializer):
    entries = LeaderboardEntrySerializer(many=True, read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = ['id', 'name', 'period', 'entries', 'is_active']
