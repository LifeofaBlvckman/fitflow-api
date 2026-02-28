from django.db import models
from django.conf import settings
from workouts.models import WorkoutSession

class Friend(models.Model):
    """Friend/follow relationship between users"""
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='following'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} follows {self.to_user.username}"

class SocialPost(models.Model):
    """Activity feed post"""
    POST_TYPES = [
        ('workout', 'Workout'),
        ('pr', 'Personal Record'),
        ('achievement', 'Achievement'),
        ('status', 'Status Update'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_posts'
    )
    post_type = models.CharField(max_length=20, choices=POST_TYPES)
    content = models.TextField(max_length=500)
    workout = models.ForeignKey(
        WorkoutSession, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='social_posts'
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s post: {self.content[:50]}"
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()

class Comment(models.Model):
    """Comments on social posts"""
    post = models.ForeignKey(
        SocialPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username}: {self.content[:30]}"

class Like(models.Model):
    """Like on social posts"""
    post = models.ForeignKey(
        SocialPost,
        on_delete=models.CASCADE,
        related_name='post_likes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f"{self.user.username} liked post {self.post.id}"

class Challenge(models.Model):
    """Fitness challenges users can join"""
    CHALLENGE_TYPES = [
        ('steps', 'Steps Challenge'),
        ('workouts', 'Workout Count'),
        ('volume', 'Total Volume'),
        ('streak', 'Streak Challenge'),
        ('weight_loss', 'Weight Loss'),
    ]
    
    DIFFICULTY = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_challenges'
    )
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY)
    target_value = models.IntegerField(help_text="Target value to achieve")
    start_date = models.DateField()
    end_date = models.DateField()
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ChallengeParticipant',
        related_name='joined_challenges'
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def participants_count(self):
        return self.participants.count()

class ChallengeParticipant(models.Model):
    """Tracks user progress in challenges"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    current_value = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'challenge')
    
    @property
    def progress_percentage(self):
        if self.challenge.target_value > 0:
            return min(100, int((self.current_value / self.challenge.target_value) * 100))
        return 0

class Leaderboard(models.Model):
    """Weekly/Monthly leaderboards"""
    PERIODS = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]
    
    name = models.CharField(max_length=100)
    period = models.CharField(max_length=20, choices=PERIODS)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.period}"

class LeaderboardEntry(models.Model):
    """Individual entries on leaderboards"""
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE, related_name='entries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.IntegerField()
    rank = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['rank']
        unique_together = ('leaderboard', 'user')
    
    def __str__(self):
        return f"{self.user.username}: #{self.rank}"
