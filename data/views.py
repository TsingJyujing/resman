from io import BytesIO
from uuid import uuid1

import magic
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from data.models import ImageThread, ReactionImageThread, DefaultS3Image
from data.serializers import ImageThreadSerializer
from resman.settings import DEFAULT_S3_BUCKET
from utils.storage import create_default_minio_client


class ImageThreadViewSet(ModelViewSet):
    """
    ViewSet for Project
    """

    serializer_class = ImageThreadSerializer
    permission_classes = [IsAuthenticated]

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

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        title = self.request.query_params.get("title")
        rs = ImageThread.objects.filter()
        if title is not None:
            rs = rs.filter(title=title)
        return rs


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
        order = int(data.get("order", "0"))
        mc = create_default_minio_client()
        if "bucket" in data and "object_name" in data:
            bucket = data["bucket"]
            object_name: str = data["object_name"]
            if bucket == DEFAULT_S3_BUCKET:
                raise KeyError(f"Can't use default bucket {DEFAULT_S3_BUCKET}")
            im_obj = DefaultS3Image.objects.create(
                bucket=bucket,
                object_name=object_name,
                thread=image_thread,
                order=order,
                content_type=(
                    magic.from_buffer(
                        mc.get_object(bucket, object_name).data,
                        mime=True
                    ) if not (
                            object_name.lower().endswith("jpg") or
                            object_name.lower().endswith("jpeg")
                    ) else "image/jpeg"
                )
            )
        else:
            object_name = f"image/{uuid1().hex}"
            file_count = len(request.FILES)
            if file_count != 1:
                raise Exception(f"Request with {file_count} file(s) is not supported")
            fp: UploadedFile = next(request.FILES.values())
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
                order=order,
                content_type=fp.content_type
            )
        return Response({"image_id": im_obj.id})


class GetImageDataView(APIView):
    def get(self, request: Request, image_id: int):
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
            # TODO return a designed 404 image
            return Response(status=404)
