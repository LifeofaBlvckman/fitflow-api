from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class Notification(models.Model):
    """
    Notification model for user interactions
    """
    # Notification types
    LIKE = 'like'
    COMMENT = 'comment'
    FOLLOW = 'follow'
    ACHIEVEMENT = 'achievement'
    
    NOTIFICATION_TYPES = (
        (LIKE, 'Like'),
        (COMMENT, 'Comment'),
        (FOLLOW, 'Follow'),
        (ACHIEVEMENT, 'Achievement'),
    )
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actor_notifications'
    )
    verb = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # For generic relation to target object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')
    
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.actor.username} {self.verb} for {self.recipient.username}"
    
    def mark_as_read(self):
        self.read = True
        self.save()
    
    @classmethod
    def create_notification(cls, actor, recipient, verb, target=None):
        """Create a notification"""
        notification = cls.objects.create(
            recipient=recipient,
            actor=actor,
            verb=verb,
            target=target
        )
        return notification
