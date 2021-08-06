import logging
from abc import abstractmethod
from typing import Any, Dict, Iterator

from django.db import models
from minio.deleteobjects import DeleteObject
from tqdm import tqdm
from whoosh import writing
from whoosh.fields import Schema, ID, TEXT

from resman.settings import DEFAULT_S3_BUCKET
from utils.nlp.word_cut import get_analyzer, clean_up_chinese_str
from utils.search_engine import ISearchable, WHOOSH_SEARCH_ENGINE
from utils.storage import create_default_minio_client, read_range, read_range_stream, get_size

log = logging.getLogger(__file__)


class BaseReaction(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    positive_reaction = models.BooleanField()
    owner = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['owner', 'thread'])
        ]
        unique_together = ('owner', 'thread')


class ReactionToImageList(BaseReaction):
    """
    The user's reaction to some image thread
    positive_reaction: is this reaction positive?
        Like: True
        Dislike: False
    """

    thread = models.ForeignKey(
        "ImageList", on_delete=models.CASCADE
    )

    class Meta(BaseReaction.Meta): pass


class ReactionToVideoList(BaseReaction):
    """
    The user's reaction to some image thread
    positive_reaction: is this reaction positive?
        Like: True
        Dislike: False
    """

    thread = models.ForeignKey(
        "VideoList", on_delete=models.CASCADE
    )

    class Meta(BaseReaction.Meta): pass


class ReactionToNovel(BaseReaction):
    """
    The user's reaction to some image thread
    positive_reaction: is this reaction positive?
        Like: True
        Dislike: False
    """

    thread = models.ForeignKey(
        "Novel", on_delete=models.CASCADE
    )

    class Meta(BaseReaction.Meta): pass


class ImageList(models.Model, ISearchable):

    @classmethod
    def get_schema(cls) -> Schema:
        return Schema(
            id=ID(unique=True, stored=True),
            title=TEXT(analyzer=get_analyzer()),
            full_text=TEXT(analyzer=get_analyzer()),
        )

    @classmethod
    def get_index_name(cls) -> str:
        return "image"

    def to_fields(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "title": clean_up_chinese_str(self.title),
            "full_text": clean_up_chinese_str(self.title + self.description),
        }

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    data = models.TextField(default="{}")
    owner = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True
    )


class BaseImage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField()
    thread = models.ForeignKey("ImageList", on_delete=models.SET_NULL, null=True)
    content_type = models.CharField(max_length=60, default="image/jpeg")

    @abstractmethod
    def get_image_data(self) -> bytes: pass

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['thread'])
        ]
        ordering = ["order", "id"]


class BaseS3Object(models.Model):
    bucket = models.CharField(max_length=255, default=DEFAULT_S3_BUCKET)
    object_name = models.CharField(max_length=255)

    def get_size(self) -> int:
        return get_size(self.bucket, self.object_name)

    def read_range_stream(self, start_byte: int = 0, end_byte: int = None) -> Iterator[bytes]:
        return read_range_stream(self.bucket, self.object_name, start_byte, end_byte)

    def read_range(self, start_byte: int = 0, end_byte: int = None) -> bytes:
        return read_range(self.bucket, self.object_name, start_byte, end_byte)

    @staticmethod
    def clean_objects(queryset):
        # Only delete bucket is default bucket
        objects_to_remove = [
            DeleteObject(obj.object_name)
            for obj in queryset.filter(bucket=DEFAULT_S3_BUCKET)
        ]
        log.info(f"Removing {len(objects_to_remove)} items in S3 storage")
        errs = create_default_minio_client().remove_objects(
            DEFAULT_S3_BUCKET,
            objects_to_remove
        )
        for err in errs:
            log.warning(f"Error while removing object: {err}")
        queryset.delete()

    class Meta:
        abstract = True


class S3Image(BaseImage, BaseS3Object):
    """
    Get image from default S3 bucket
    """
    bucket = models.CharField(max_length=255)
    object_name = models.CharField(max_length=255)

    def get_image_data(self) -> bytes:
        return self.read_range()

    @staticmethod
    def clean_dangling_objects():
        BaseS3Object.clean_objects(S3Image.objects.filter(thread=None))


class VideoList(models.Model, ISearchable):

    @classmethod
    def get_schema(cls) -> Schema:
        return Schema(
            id=ID(unique=True, stored=True),
            full_text=TEXT(analyzer=get_analyzer()),
        )

    @classmethod
    def get_index_name(cls) -> str:
        return "video"

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
        on_delete=models.SET_NULL,
        null=True
    )


class S3Video(BaseS3Object):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)
    thread = models.ForeignKey("VideoList", on_delete=models.SET_NULL, null=True)

    @staticmethod
    def clean_dangling_objects():
        BaseS3Object.clean_objects(S3Video.objects.filter(thread=None))

    class Meta:
        indexes = [
            models.Index(fields=['thread'])
        ]
        ordering = ["order", "id"]


class Novel(BaseS3Object, ISearchable):

    @classmethod
    def get_schema(cls) -> Schema:
        return Schema(
            id=ID(unique=True, stored=True),
            title=TEXT(analyzer=get_analyzer()),
            full_text=TEXT(analyzer=get_analyzer()),
        )

    @classmethod
    def get_index_name(cls) -> str:
        return "novel"

    def to_fields(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "title": clean_up_chinese_str(self.title),
            "full_text": clean_up_chinese_str(self.read_range().decode())
        }

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    data = models.TextField(default="{}")
    owner = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True
    )


class Event(models.Model):
    """
    For more details, see README.md
    """
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True
    )
    # Event Types: impression/page_view/fetch_media/...
    event_type = models.CharField(max_length=100)
    # Media Type: Novel/VideoList/ImageList
    media_type = models.CharField(max_length=100)
    data = models.TextField(default="{}")

    class Meta:
        indexes = [
            models.Index(fields=['created']),
            models.Index(fields=['user', 'event_type', 'media_type']),
        ]


def rebuild_searchable_index(cls):
    ix = WHOOSH_SEARCH_ENGINE.get_index(cls.get_index_name(), cls.get_schema())
    with ix.writer() as w:
        w.mergetype = writing.CLEAR
    with ix.writer() as w:
        for obj in tqdm(cls.objects.all()):
            w.add_document(**obj.to_fields())


def rebuild_all_index():
    # List of ISearchable classes
    for cls in [VideoList, ImageList, Novel]:
        rebuild_searchable_index(cls)
