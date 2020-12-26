from rest_framework.serializers import ModelSerializer

from data.models import ImageThread


class ImageThreadSerializer(ModelSerializer):
    """
    Serializer for ImageThread
    """

    class Meta:
        model = ImageThread
        fields = [
            "id",
            "created",
            "updated",
            "title",
            "description",
            "data",
            "owner"
        ]
