from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.
class Question(models.Model):
    sender = models.CharField(max_length=100)
    data = JSONField()
    timestamp = models.DateTimeField('date created', auto_now_add=True)

class Answer(models.Model):
    sender = models.CharField(max_length=100)
    data = JSONField()
    timestamp = models.DateTimeField('date created', auto_now_add=True)
