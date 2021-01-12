import json

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from data.models import ImageThread


class ImageThreadSerializer(ModelSerializer):
    """
    Serializer for ImageThread
    """

    data = serializers.JSONField(allow_null=True, default={})

    def validate_data(self, data):
        return json.dumps(data)

    def to_representation(self, instance):
        data = super(ImageThreadSerializer, self).to_representation(instance)
        data["data"] = json.loads(data["data"])
        return data

    class Meta:
        model = ImageThread
        fields = [
            "id",
            "created",
            "updated",
            "title",
            "description",
            "owner",
            "data"
        ]
