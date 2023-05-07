import json

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from data.models import ImageList, Novel, Tag, VideoList


class JSONDataSerializer(ModelSerializer):
    """
    The field save as Text but actually JSON
    For saving JSON data compatible with SQLite3
    """

    data = serializers.JSONField(allow_null=True, default={})

    # noinspection PyMethodMayBeStatic
    def validate_data(self, data):
        return json.dumps(data)

    def to_representation(self, instance):
        data = super(JSONDataSerializer, self).to_representation(instance)
        if isinstance(data["data"], str):
            data["data"] = json.loads(data["data"])
        return data


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "text"]


class ImageListSerializer(JSONDataSerializer):
    """
    Serializer for ImageList
    """

    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = ImageList
        fields = [
            "id",
            "created",
            "updated",
            "title",
            "description",
            "owner",
            "data",
            "tags",
        ]


class VideoListSerializer(JSONDataSerializer):
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = VideoList
        fields = [
            "id",
            "created",
            "updated",
            "title",
            "description",
            "owner",
            "data",
            "tags",
        ]


class NovelSerializer(JSONDataSerializer):
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = Novel
        fields = [
            "id",
            "created",
            "updated",
            "title",
            "owner",
            "data",
            "tags",
        ]
