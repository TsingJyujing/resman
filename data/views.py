from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from data.models import ImageThread
from data.serializers import ImageThreadSerializer


class ImageThreadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project
    """

    serializer_class = ImageThreadSerializer
    permission_classes = (
        IsAuthenticated
    )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return ImageThread.objects.filter()
