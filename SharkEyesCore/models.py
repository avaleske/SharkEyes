from django.db import models

class FeedbackHistory (models.Model):
    feedback_title = models.CharField(max_length=255)
    feedback_comments = models.CharField(max_length=255)
