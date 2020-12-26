from django.urls import include, path
from rest_framework.routers import DefaultRouter

from data.views import ImageThreadViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"image_thread", viewset=ImageThreadViewSet, basename="image_thread")

urlpatterns = [
    path("auth", include("rest_framework.urls")),
    path("", include(router.urls)),
]
