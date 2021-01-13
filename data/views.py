import logging
import os
import time
from io import BytesIO
from typing import Sequence
from uuid import uuid1

import magic
from django.core.paginator import Paginator
from django.db.models import Case, When
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from whoosh.fields import Schema

from data.models import ImageThread, ReactionImageThread, DefaultS3Image
from data.serializers import ImageThreadSerializer
from resman.settings import DEFAULT_S3_BUCKET, FRONTEND_STATICFILES_DIR
from utils.search_engine import WhooshSearchableModelViewSet, parse_title_query
from utils.storage import create_default_minio_client, get_default_minio_client

log = logging.getLogger(__file__)


# Image Operations


# noinspection PyMethodOverriding
class ImageThreadViewSet(WhooshSearchableModelViewSet):
    """
    ViewSet for Project
    """

    serializer_class = ImageThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_index_name(self) -> str:
        return ImageThread.get_index_name()

    def get_schema(self) -> Schema:
        return ImageThread.get_schema()

    def retrieve(self, request, *args, **kwargs):
        instance: ImageThread = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        reaction: ReactionImageThread = ReactionImageThread.objects.filter(
            owner=self.request.user,
            thread=instance
        ).first()
        data["positive_reaction"] = None if reaction is None else reaction.positive_reaction
        data["like_count"] = ReactionImageThread.objects.filter(
            owner=self.request.user,
            thread=instance,
            positive_reaction=True
        ).count()
        data["dislike_count"] = ReactionImageThread.objects.filter(
            owner=self.request.user,
            thread=instance,
            positive_reaction=False
        ).count()
        data["images"] = list(
            im.id for im in DefaultS3Image.objects.filter(thread=instance)
        )
        return Response(data)

    def destroy(self, request, pk=None):
        response = super().destroy(request, pk=pk)
        log.info(f"Cleaning dangling images after deleted image thread {pk}")
        DefaultS3Image.clean_dangling_objects()
        return response

    def list(self, request: Request):
        q = request.query_params.get("q")
        n = int(request.query_params.get("n", "20"))
        p = int(request.query_params.get("p", "1"))
        connector = request.query_params.get("a", "andmaybe")
        if q is not None:
            qr = parse_title_query("full_text", q, 10, connector)
            with self.get_searcher() as s:
                indexes: Sequence[int] = [int(hit["id"]) for hit in s.search(qr, limit=p * n)][(p - 1) * n:]
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(indexes)])
            queryset = ImageThread.objects.filter(pk__in=indexes).order_by(preserved)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            queryset = Paginator(queryset, n).page(p)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return ImageThread.objects.order_by("-created")


class UserReactionView(APIView):
    def post(self, request: Request, image_thread_id: int):
        positive_reaction = self.request.data["positive_reaction"]
        rit: ReactionImageThread = ReactionImageThread.objects.filter(
            owner=self.request.user,
            thread=ImageThread.objects.get(id=image_thread_id)
        ).first()

        if rit is not None:
            if positive_reaction is not None:
                rit.positive_reaction = positive_reaction
                rit.save()
            else:
                rit.delete()
        elif positive_reaction is not None:
            ReactionImageThread.objects.create(
                owner=self.request.user,
                thread=ImageThread.objects.get(id=image_thread_id),
                positive_reaction=positive_reaction
            )

        return Response({
            "positive_reaction": positive_reaction,
        })

    def get(self, request: Request, image_thread_id: int):
        positive_reaction = None
        rit = ReactionImageThread.objects.filter(
            owner=self.request.user,
            thread=ImageThread.objects.get(id=image_thread_id)
        ).first()
        if rit is not None:
            positive_reaction = rit.positive_reaction
        return Response({
            "positive_reaction": positive_reaction,
        })


class UploadS3ImageView(APIView):
    def post(self, request: Request):
        data = request.data
        image_thread_id = int(data["image_thread_id"])
        image_thread = ImageThread.objects.get(id=image_thread_id)
        mc = get_default_minio_client()
        start_time = time.time()
        image_id_list = []
        if "default_s3_files" in data:
            for s3_file in data["default_s3_files"]:
                bucket: str = s3_file["bucket"]
                object_name: str = s3_file["object_name"]
                order: int = int(s3_file["order"])
                if bucket == DEFAULT_S3_BUCKET:
                    raise KeyError(f"Can't use default bucket {DEFAULT_S3_BUCKET}")
                object_name_lower = object_name.lower()
                if object_name_lower.endswith("jpg") or object_name_lower.endswith("jpeg"):
                    content_type = "image/jpeg"
                elif object_name_lower.endswith("png"):
                    content_type = "image/png"
                elif object_name_lower.endswith("gif"):
                    content_type = "image/gif"
                else:
                    log.warning(f"Can't guess content type from {bucket}:{object_name}, detecting...")
                    content_type = magic.from_buffer(
                        mc.get_object(bucket, object_name).data,
                        mime=True
                    )
                im_obj = DefaultS3Image.objects.create(
                    bucket=bucket,
                    object_name=object_name,
                    thread=image_thread,
                    order=order,
                    content_type=content_type
                )
                image_id_list.append(im_obj.id)
        else:
            for fn, fp in request.FILES.items():
                object_name = f"image/{uuid1().hex}"
                file_data = fp.read()
                mc.put_object(
                    DEFAULT_S3_BUCKET, object_name,
                    BytesIO(file_data), len(file_data),
                    content_type=fp.content_type
                )
                im_obj = DefaultS3Image.objects.create(
                    bucket=DEFAULT_S3_BUCKET,
                    object_name=object_name,
                    thread=image_thread,
                    order=int(fn),
                    content_type=fp.content_type
                )
                image_id_list.append(im_obj.id)
        log.info(f"Request finished in {int((time.time() - start_time) * 1000)} ms")
        return Response({"image_id_list": image_id_list})


class GetImageDataView(APIView):
    with open(os.path.join(FRONTEND_STATICFILES_DIR, "img/404.png"), "rb") as fp:
        IMAGE_404_DATA = fp.read()
    IMAGE_404_CONTENT_TYPE = magic.from_buffer("image/png", mime=True)

    def get(self, request: Request, image_id: int):
        # TODO Using cache here
        try:
            im: DefaultS3Image = DefaultS3Image.objects.get(id=image_id)
            file_object = create_default_minio_client().get_object(
                im.bucket,
                im.object_name,
            )
            return HttpResponse(
                content=file_object.data,
                content_type=file_object.headers.get("Content-Type", im.content_type)
            )
        except DefaultS3Image.DoesNotExist:
            resp = HttpResponse(
                content=GetImageDataView.IMAGE_404_DATA,
                content_type=GetImageDataView.IMAGE_404_CONTENT_TYPE,
            )
            resp.status_code = status.HTTP_404_NOT_FOUND
            return resp
