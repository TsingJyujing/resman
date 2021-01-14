import logging
from abc import abstractmethod
from typing import Any, Dict

from django.db import models
from minio.deleteobjects import DeleteObject
from tqdm import tqdm
from whoosh import writing
from whoosh.fields import Schema, ID, TEXT

from resman.settings import DEFAULT_S3_BUCKET
from utils.nlp.word_cut import get_analyzer, clean_up_chinese_str
from utils.search_engine import ISearchable, WHOOSH_SEARCH_ENGINE
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
        indexes = [
            models.Index(fields=['owner', 'thread'])
        ]
        unique_together = ('owner', 'thread')


class ImageThread(models.Model, ISearchable):

    @classmethod
    def get_schema(cls) -> Schema:
        return Schema(
            id=ID(unique=True, stored=True),
            full_text=TEXT(analyzer=get_analyzer()),
        )

    @classmethod
    def get_index_name(cls) -> str:
        return "imagethread"

    def to_fields(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "full_text": clean_up_chinese_str(self.title + self.description),
        }

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    data = models.TextField(default="{}")
    owner = models.ForeignKey(
        "auth.User",
        related_name="image_thread",
        on_delete=models.SET_NULL,
        null=True
    )


def rebuild_image_thread_index():
    ix = WHOOSH_SEARCH_ENGINE.get_index(ImageThread.get_index_name(), ImageThread.get_schema())
    with ix.writer() as w:
        w.mergetype = writing.CLEAR
    with ix.writer() as w:
        for obj in tqdm(ImageThread.objects.all()):
            w.add_document(**obj.to_fields())


class BaseImage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField()
    thread = models.ForeignKey("ImageThread", on_delete=models.SET_NULL, null=True)
    content_type = models.CharField(max_length=60, default="image/jpeg")

    @abstractmethod
    def get_image_data(self) -> bytes: pass

    class Meta:
        indexes = [
            models.Index(fields=['thread'])
        ]
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
    def clean_dangling_objects():
        objects_to_remove = [
            DeleteObject(obj.object_name)
            for obj in DefaultS3Image.objects.filter(thread=None, bucket=DEFAULT_S3_BUCKET)
        ]
        log.info(f"Removing {len(objects_to_remove)} items in S3 server")
        errs = create_default_minio_client().remove_objects(
            DEFAULT_S3_BUCKET,
            objects_to_remove
        )
        for err in errs:
            log.warning(f"Error while removing object: {err}")
        DefaultS3Image.objects.filter(thread=None).delete()


# VIDEO THREAD RELATED
class VideoThread(models.Model, ISearchable):

    @classmethod
    def get_schema(cls) -> Schema:
        return Schema(
            id=ID(unique=True, stored=True),
            full_text=TEXT(analyzer=get_analyzer()),
        )

    @classmethod
    def get_index_name(cls) -> str:
        return "videothread"

    def to_fields(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "full_text": clean_up_chinese_str(self.title + self.description),
        }

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    data = models.TextField(default="{}")
    owner = models.ForeignKey(
        "auth.User",
        related_name="video_thread",
        on_delete=models.SET_NULL,
        null=True
    )


class DefaultS3Video(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)
    thread = models.ForeignKey("VideoThread", on_delete=models.SET_NULL, null=True)
    bucket = models.CharField(max_length=255)
    object_name = models.CharField(max_length=255)

    @staticmethod
    def clean_dangling_objects():
        objects_to_remove = [
            DeleteObject(obj.object_name)
            for obj in DefaultS3Video.objects.filter(thread=None, bucket=DEFAULT_S3_BUCKET)
        ]
        log.info(f"Removing {len(objects_to_remove)} items in S3 server")
        errs = create_default_minio_client().remove_objects(
            DEFAULT_S3_BUCKET,
            objects_to_remove
        )
        for err in errs:
            log.warning(f"Error while removing object: {err}")
        DefaultS3Video.objects.filter(thread=None).delete()

    class Meta:
        indexes = [
            models.Index(fields=['thread'])
        ]
        abstract = True
        ordering = ["order", "id"]


# NOVEL THREAD RELATED
class NovelThread(models.Model, ISearchable):

    @classmethod
    def get_schema(cls) -> Schema:
        return Schema(
            id=ID(unique=True, stored=True),
            title=TEXT(analyzer=get_analyzer()),
            full_text=TEXT(analyzer=get_analyzer()),
        )

    @classmethod
    def get_index_name(cls) -> str:
        return "videothread"

    def to_fields(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            # TODO read data from S3 as full_text
            "title": clean_up_chinese_str(self.title),
        }

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)

    # MUST save in default bucket
    object_name = models.CharField(max_length=255)

    data = models.TextField(default="{}")

    owner = models.ForeignKey(
        "auth.User",
        related_name="video_thread",
        on_delete=models.SET_NULL,
        null=True
    )
