from django.urls import path

from . import views

app_name = "videos"

urlpatterns = [
    path("file/<int:video_id>", views.stream_video)
]
