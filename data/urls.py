from django.urls import include, path
from rest_framework.routers import DefaultRouter

from data.views import (
    ExpandSearchByW2V,
    GetImageDataViewWithCache,
    GetNovelPage,
    GetVideoStream,
    ImageListTagOperation,
    ImageListUserReactionView,
    ImageListViewSet,
    NovelTagOperation,
    NovelUserReactionView,
    NovelViewSet,
    RecommendImageList,
    StorageReport,
    UploadS3ImageView,
    UploadS3VideoView,
    VideoListTagOperation,
    VideoListUserReactionView,
    VideoListViewSet,
)
from resman.settings import DEBUG

router = DefaultRouter(trailing_slash=False)
router.register(r"imagelist", viewset=ImageListViewSet, basename="imagelist")
router.register(r"videolist", viewset=VideoListViewSet, basename="videolist")
router.register(r"novel", viewset=NovelViewSet, basename="novel")
urlpatterns = [
    path("auth", include("rest_framework.urls")),
    path("imagelist/<int:thread_id>/tags/<str:tag>", ImageListTagOperation.as_view()),
    path("videolist/<int:thread_id>/tags/<str:tag>", VideoListTagOperation.as_view()),
    path("novel/<int:thread_id>/tags/<str:tag>", NovelTagOperation.as_view()),
    path("imagelist/<int:thread_id>/reaction", ImageListUserReactionView.as_view()),
    path("videolist/<int:thread_id>/reaction", VideoListUserReactionView.as_view()),
    path("novel/<int:thread_id>/reaction", NovelUserReactionView.as_view()),
    path("image/<int:image_id>", GetImageDataViewWithCache.as_view()),
    path("video/<int:video_id>", GetVideoStream.as_view()),
    path("novel/<int:novel_id>/data", GetNovelPage.as_view()),
    path("image/upload", UploadS3ImageView.as_view()),
    path("video/upload", UploadS3VideoView.as_view()),
    path("nlp/query_expand", ExpandSearchByW2V.as_view()),
    path("recsys/imagelist", RecommendImageList.as_view()),
]
if DEBUG:
    urlpatterns.append(
        path("developer/storage/report", StorageReport.as_view()),
    )
urlpatterns.append(
    path("", include(router.urls)),
)
