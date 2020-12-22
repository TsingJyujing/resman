import json
from abc import abstractmethod
from django.contrib import auth
from django.db import models


# Image thread
class ReactionImageThread(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # Like: True Dislike: False
    positive_reaction = models.BooleanField()
    owner = models.ForeignKey(
        "auth.User", related_name="like_image", on_delete=models.CASCADE
    )
    thread = models.ForeignKey(
        "ImageThread", related_name="like_image", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('owner', 'thread')


class ImageThread(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    data = models.TextField(default="{}")

    def set_data(self, x):
        self.data = json.dumps(x)

    def get_data(self):
        return json.loads(self.data)


class BaseImage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField()
    thread = models.ForeignKey("ImageThread", on_delete=models.CASCADE)

    @abstractmethod
    def get_image_data(self) -> bytes: pass

    class Meta:
        abstract = True
        ordering = ["order"]


class DefaultS3Image(BaseImage):
    """
    Get image from default S3 bucket
    """
    s3_path = models.CharField(max_length=255, unique=True)

    def get_image_data(self) -> bytes:
        pass

# Video Thread

# Novel Thread
