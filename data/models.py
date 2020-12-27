import logging
from abc import abstractmethod

from django.db import models
from minio.deleteobjects import DeleteObject

from resman.settings import DEFAULT_S3_BUCKET
from utils.storage import create_default_minio_client

log = logging.getLogger(__file__)


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
    thread = models.ForeignKey("ImageThread", on_delete=models.SET_NULL, null=True)
    content_type = models.CharField(max_length=60, default="image/jpeg")

    @abstractmethod
    def get_image_data(self) -> bytes: pass

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class DefaultS3Image(BaseImage):
    """
    Get image from default S3 bucket
    """
    bucket = models.CharField(max_length=255)
    object_name = models.CharField(max_length=255)

    def get_image_data(self) -> bytes:
        return create_default_minio_client().get_object(self.bucket, self.object_name).data

    @staticmethod
    def clean_wild_objects():
        errs = create_default_minio_client().remove_objects(
            DEFAULT_S3_BUCKET,
            [
                DeleteObject(obj.object_name)
                for obj in DefaultS3Image.objects.filter(thread=None, bucket=DEFAULT_S3_BUCKET)
            ]
        )
        for err in errs:
            log.warning(f"Error while removing object: {err}")
        DefaultS3Image.objects.filter(thread=None).delete()

    def delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)

# VIDEO THREAD RELATED

# NOVEL THREAD RELATED
