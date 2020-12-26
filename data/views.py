# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from data.models import ImageThread
from data.serializers import ImageThreadSerializer


class ImageThreadViewSet(ModelViewSet):
    """
    ViewSet for Project
    """

    serializer_class = ImageThreadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        title = self.request.query_params.get("title")
        rs = ImageThread.objects.filter()
        if title is not None:
            rs = rs.filter(title=title)
        return rs

# class UserReactionView(APIView):
