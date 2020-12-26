from abc import abstractmethod

from django.db import models
from tsing_spider.util.pyurllib import http_get

from utils.storage import DEFAULT_MINIO_CLIENT


class BaseThread(models.Model):
    class Meta:
        abstract = True
        ordering = ["order"]


# IMAGE THREAD RELATED

class ReactionImageThread(models.Model):
    """
    The user's reaction to some image thread
    positive_reaction: is this reaction positive?
        Like: True
        Dislike: False
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
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
    data = models.JSONField()
    owner = models.ForeignKey(
        "auth.User",
        related_name="image_thread",
        on_delete=models.SET_NULL,
        null=True
    )


class BaseImage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField()
    thread = models.ForeignKey("ImageThread", on_delete=models.CASCADE)

    @abstractmethod
    def get_image_data(self) -> bytes: pass

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class HttpImage(BaseImage):
    """
    Get image from HTTP URL
    """
    url = models.TextField()

    def get_image_data(self) -> bytes:
        return http_get(self.url)


class DefaultS3Image(BaseImage):
    """
    Get image from default S3 bucket
    """
    bucket = models.CharField(max_length=255)
    object_name = models.CharField(max_length=255)

    def get_image_data(self) -> bytes:
        return DEFAULT_MINIO_CLIENT.get_object(self.bucket, self.object_name).data

# VIDEO THREAD RELATED

# NOVEL THREAD RELATED
