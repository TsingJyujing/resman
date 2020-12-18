from data.models import ImageThread


class ImageThreadSerializer(object):
    """
    Serializer for ImageThread
    """

    class Meta:
        model = ImageThread
        fields = [
            "id", "created", "updated",
            "title", "description", "data"
        ]
