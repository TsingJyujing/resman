from django.urls import include, path
from rest_framework.routers import DefaultRouter

from data.views import ImageThreadViewSet, UserReactionView, UploadS3ImageView, GetImageDataView

router = DefaultRouter(trailing_slash=False)
router.register(r"image_thread", viewset=ImageThreadViewSet, basename="image_thread")

urlpatterns = [
    path("auth", include("rest_framework.urls")),
    path("", include(router.urls)),
    path("image_thread/<int:image_thread_id>/reaction", UserReactionView.as_view()),
    path("image/upload", UploadS3ImageView.as_view()),
    path("image/<int:image_id>", GetImageDataView.as_view()),
]
