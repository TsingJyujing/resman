import json

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from data.models import ImageList, VideoList, Novel


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


class ImageListSerializer(JSONDataSerializer):
    """
    Serializer for ImageList
    """

    class Meta:
        model = ImageList
        fields = [
            "id",
            "created",
            "updated",
            "title",
            "description",
            "owner",
            "data"
        ]


class VideoListSerializer(JSONDataSerializer):
    class Meta:
        model = VideoList
        fields = [
            "id",
            "created",
            "updated",
            "title",
            "description",
            "owner",
            "data"
        ]


class NovelSerializer(JSONDataSerializer):
    class Meta:
        model = Novel
        fields = [
            "id",
            "created",
            "updated",
            "title",
            "owner",
            "data"
        ]
