from django.db import models
from django_mysql.models import JSONField

# Create your models here.
class Video(models.Model):
    title = models.TextField()
    add_time = models.DateTimeField(auto_now_add=True)
    external_info = JSONField()

    def __str__(self):
        return self.title
