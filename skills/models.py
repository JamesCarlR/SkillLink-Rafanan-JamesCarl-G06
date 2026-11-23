from django.db import models
from django.conf import settings

class SkillPost(models.Model):
    SKILL_TYPES = [
        ('TEACH', 'I can teach this'),
        ('LEARN', 'I want to learn this'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    title = models.CharField(max_length=100)
    description = models.TextField()
    skill_type = models.CharField(max_length=10, choices=SKILL_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.skill_type})"