import datetime
import json
import logging
import mimetypes
import os
import pickle
import re
import time
from abc import abstractmethod
from functools import lru_cache, reduce
from io import BytesIO
from math import ceil
from typing import Sequence, Tuple, List
from uuid import uuid1

import magic
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Case, When
from django.db.models import Q
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from whoosh.fields import Schema
from whoosh.query import Term
from whoosh.query.compound import Or

from data.models import ImageList, ReactionToImageList, S3Image, VideoList, S3Video, ReactionToVideoList, Novel, \
    ReactionToNovel, Event
from data.serializers import ImageListSerializer, VideoListSerializer, NovelSerializer
from resman.settings import DEFAULT_S3_BUCKET, FRONTEND_STATICFILES_DIR, IMAGE_CACHE_SIZE, RECSYS_MODEL_PATH
from utils.nlp.w2v_search import title_expand
from utils.recsys.lr_recsys import train_model, get_aggregated_logs
from utils.search_engine import WhooshSearchableModelViewSet, parse_title_query
from utils.storage import create_default_minio_client, get_default_minio_client

log = logging.getLogger(__file__)


# noinspection PyMethodOverriding
class MediaViewSet(WhooshSearchableModelViewSet):

    @abstractmethod
    def get_searchable_class(self):
        pass

    @abstractmethod
    def get_reaction_class(self):
        pass

    def get_index_name(self) -> str:
        return self.get_searchable_class().get_index_name()

    def get_schema(self) -> Schema:
        return self.get_searchable_class().get_schema()

    def serialize_with_reaction(self, instance, user):
        serializer = self.get_serializer(instance)
        data = serializer.data
        reaction = self.get_reaction_class().objects.filter(
            owner=user,
            thread=instance
        ).first()
        data["positive_reaction"] = None if reaction is None else reaction.positive_reaction
        data["like_count"] = self.get_reaction_class().objects.filter(
            owner=user,
            thread=instance,
            positive_reaction=True
        ).count()
        data["dislike_count"] = self.get_reaction_class().objects.filter(
            owner=user,
            thread=instance,
            positive_reaction=False
        ).count()
        Event.objects.create(
            user=user,
            event_type="page_view",
            media_type=self.get_searchable_class().__name__,
            data=json.dumps(dict(
                id=data["id"],
            ))
        )
        return data

    def list(self, request: Request):
        """
        Core of search engine
        :param request:
        :return:
        """
        # TODO 需要整理一下这个超级大函数
        query = request.query_params.get("q")
        if query == "":
            query = None
        page_size = int(request.query_params.get("n", "20"))
        page_id = int(request.query_params.get("p", "1"))
        similar_words = int(request.query_params.get("sw", "10"))
        like_only = request.query_params.get("lo") is not None
        search_field = request.query_params.get("f", "full_text")
        connector = request.query_params.get("a", "andmaybe")

        if query is not None and not connector.startswith("contains"):
            qr = parse_title_query(search_field, query, similar_words, connector)
            liked_matcher = None
            if like_only:
                liked_matcher = Or([
                    Term("id", str(reaction.thread.id))
                    for reaction in self.get_reaction_class().objects.filter(
                        positive_reaction=True
                    ).filter(
                        owner=request.user
                    )
                ])

            with self.get_searcher() as s:
                indexes: Sequence[int] = [
                                             int(hit["id"])
                                             for hit in s.search(qr, filter=liked_matcher, limit=page_id * page_size)
                                         ][(page_id - 1) * page_size:]
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(indexes)])
            queryset = self.get_searchable_class().objects.filter(pk__in=indexes).order_by(preserved)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            if like_only:
                queryset = queryset.filter(
                    id__in=list(
                        reaction.thread.id
                        for reaction in self.get_reaction_class().objects.filter(
                            positive_reaction=True
                        ).filter(
                            owner=request.user
                        )
                    )
                )
            qs = []
            for ws in re.split(r"\s+", query or ""):
                if ws != "":
                    cq = Q(title__contains=ws)
                    if self.get_searchable_class() != Novel:
                        cq = cq | Q(description__contains=ws)
                    if similar_words > 0:
                        for similar_word, _ in title_expand(ws, similar_words):
                            cq = cq | Q(title__contains=similar_word)
                            if self.get_searchable_class() != Novel:
                                cq = cq | Q(description__contains=similar_word)
                    qs.append(cq)

            if len(qs) > 0:
                if connector == "contains_or":
                    queryset = queryset.filter(
                        reduce(lambda q1, q2: q1 | q2, qs)
                    )
                elif connector == "contains_and":
                    queryset = queryset.filter(
                        reduce(lambda q1, q2: q1 & q2, qs)
                    )
                else:
                    raise Exception(f"Unknown connector {connector}")
            queryset = Paginator(queryset, page_size).page(page_id)
        serialized_data = self.get_serializer(queryset, many=True).data
        # Rank again by RecSys model
        Event.objects.create(
            user=request.user,
            event_type="impression",
            media_type=self.get_searchable_class().__name__,
            data=json.dumps(dict(
                query=query,
                page_size=page_size,
                page_id=page_id,
                similar_words=similar_words,
                like_only=like_only,
                search_field=search_field,
                connector=connector,
                result=[row["id"] for row in serialized_data],
            ))
        )
        return Response(serialized_data)

    def get_queryset(self):
        return self.get_searchable_class().objects.order_by("-created")


# noinspection PyMethodOverriding
class ImageListViewSet(MediaViewSet):
    serializer_class = ImageListSerializer
    permission_classes = [IsAuthenticated]

    def get_searchable_class(self):
        return ImageList

    def get_reaction_class(self):
        return ReactionToImageList

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        data = self.serialize_with_reaction(instance, user)
        data["images"] = [v.id for v in S3Image.objects.filter(thread=instance)]
        return Response(data)

    def destroy(self, request, pk=None):
        response = super().destroy(request, pk=pk)
        log.info(f"Cleaning dangling images after deleted image thread {pk}")
        S3Image.clean_dangling_objects()
        return response


# noinspection PyMethodOverriding
class VideoListViewSet(MediaViewSet):
    serializer_class = VideoListSerializer
    permission_classes = [IsAuthenticated]

    def get_searchable_class(self):
        return VideoList

    def get_reaction_class(self):
        return ReactionToVideoList

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        data = self.serialize_with_reaction(instance, user)
        data["videos"] = [v.id for v in S3Video.objects.filter(thread=instance)]
        return Response(data)

    def destroy(self, request, pk=None):
        response = super().destroy(request, pk=pk)
        log.info(f"Cleaning dangling videos after deleted image thread {pk}")
        S3Video.clean_dangling_objects()
        return response


# noinspection PyMethodOverriding
class NovelViewSet(MediaViewSet):
    serializer_class = NovelSerializer
    permission_classes = [IsAuthenticated]

    def get_searchable_class(self):
        return Novel

    def get_reaction_class(self):
        return ReactionToNovel

    def perform_create(self, serializer):
        mc = get_default_minio_client()
        files = self.request.FILES
        if len(files) != 1:
            raise ValueError("More than 1 file is not allowed")
        file_data = next(files.values()).read()
        object_name = f"novel/{uuid1()}.txt"
        with BytesIO(file_data) as fp:
            mc.put_object(
                DEFAULT_S3_BUCKET,
                object_name,
                fp, len(file_data), "plain/text"
            )
        serializer.save(owner=self.request.user, bucket=DEFAULT_S3_BUCKET, object_name=object_name)
        self.search_engine_create(serializer.instance)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.serialize_with_reaction(self.get_object(), self.request.user))

    def destroy(self, request, pk=None):
        novel: Novel = Novel.objects.get(id=pk)
        get_default_minio_client().remove_object(novel.bucket, novel.object_name)
        response = super().destroy(request, pk=pk)
        return response


class BaseUserReactionView(APIView):

    @abstractmethod
    def get_object_class(self):
        pass

    @abstractmethod
    def get_reaction_class(self):
        pass

    def post(self, request: Request, thread_id: int):
        positive_reaction = self.request.data["positive_reaction"]
        reaction_of_thread = self.get_reaction_class().objects.filter(
            owner=self.request.user,
            thread=self.get_object_class().objects.get(id=thread_id)
        ).first()

        original_status = None if reaction_of_thread is None else reaction_of_thread.positive_reactio

        if reaction_of_thread is not None:
            if positive_reaction is not None:
                reaction_of_thread.positive_reaction = positive_reaction
                reaction_of_thread.save()
            else:
                reaction_of_thread.delete()
        elif positive_reaction is not None:
            self.get_reaction_class().objects.create(
                owner=self.request.user,
                thread=self.get_object_class().objects.get(id=thread_id),
                positive_reaction=positive_reaction
            )
        Event.objects.create(
            user=request.user,
            event_type="reaction",
            media_type=self.get_object_class().__name__,
            data=json.dumps(dict(
                id=thread_id,
                original_status=original_status,
                command=positive_reaction,
            ))
        )
        return Response({
            "positive_reaction": positive_reaction,
        })

    def get(self, request: Request, thread_id: int):
        positive_reaction = None
        rit = self.get_reaction_class().objects.filter(
            owner=self.request.user,
            thread=self.get_object_class().objects.get(id=thread_id),
        ).first()
        if rit is not None:
            positive_reaction = rit.positive_reaction
        return Response({
            "positive_reaction": positive_reaction,
        })


class ImageListUserReactionView(BaseUserReactionView):
    def get_object_class(self):
        return ImageList

    def get_reaction_class(self):
        return ReactionToImageList


class VideoListUserReactionView(BaseUserReactionView):
    def get_object_class(self):
        return VideoList

    def get_reaction_class(self):
        return ReactionToVideoList


class NovelUserReactionView(BaseUserReactionView):
    def get_object_class(self):
        return Novel

    def get_reaction_class(self):
        return ReactionToNovel


class UploadS3ImageView(APIView):
    def post(self, request: Request):
        data = request.data
        image_thread_id = int(data["image_list_id"])
        image_thread = ImageList.objects.get(id=image_thread_id)
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
                im_obj = S3Image.objects.create(
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
                im_obj = S3Image.objects.create(
                    bucket=DEFAULT_S3_BUCKET,
                    object_name=object_name,
                    thread=image_thread,
                    order=int(fn) if fn.isdigit() else 0,
                    content_type=fp.content_type
                )
                image_id_list.append(im_obj.id)
        log.info(f"Request finished in {int((time.time() - start_time) * 1000)} ms")
        return Response({"image_id_list": image_id_list})


class UploadS3VideoView(APIView):
    def post(self, request: Request):
        video_list = VideoList.objects.get(
            id=int(request.data["video_list_id"])
        )
        s3_video_created = []
        if "bucket" in request.data and "object_name" in request.data:
            s3_video_created.append(S3Video.objects.create(
                thread=video_list,
                bucket=request.data["bucket"],
                object_name=request.data["object_name"]
            ))
        else:
            mc = get_default_minio_client()
            for fn, fp in request.FILES.items():
                video_file_id = uuid1()
                object_name = f"video/{video_list.id}/{video_file_id}.mp4"

                mc.put_object(
                    DEFAULT_S3_BUCKET,
                    object_name,
                    fp, fp.size,
                    content_type=fp.content_type or "video/mp4"
                )

                s3_video_created.append(S3Video.objects.create(
                    thread=video_list,
                    bucket=DEFAULT_S3_BUCKET,
                    object_name=object_name
                ))

        return Response({"video_id_list": [v.id for v in s3_video_created]})


class GetImageDataView(APIView):
    with open(os.path.join(FRONTEND_STATICFILES_DIR, "img/404.png"), "rb") as fp:
        IMAGE_404_DATA = fp.read()
    IMAGE_404_CONTENT_TYPE = magic.from_buffer("image/png", mime=True)

    def get(self, request: Request, image_id: int):
        try:
            im: S3Image = S3Image.objects.get(id=image_id)
            file_object = create_default_minio_client().get_object(
                im.bucket,
                im.object_name,
            )

            Event.objects.create(
                user=request.user,
                event_type="fetch_media",
                media_type="ImageList",
                data=json.dumps(dict(
                    id=image_id,
                ))
            )

            def _wrapper():
                yield from file_object.stream()
                file_object.close()

            return StreamingHttpResponse(
                streaming_content=_wrapper(),
                content_type=file_object.headers.get("Content-Type", im.content_type)
            )
        except S3Image.DoesNotExist:
            resp = HttpResponse(
                content=GetImageDataView.IMAGE_404_DATA,
                content_type=GetImageDataView.IMAGE_404_CONTENT_TYPE,
            )
            resp.status_code = status.HTTP_404_NOT_FOUND
            return resp


class GetImageDataViewWithCache(APIView):
    with open(os.path.join(FRONTEND_STATICFILES_DIR, "img/404.png"), "rb") as fp:
        IMAGE_404_DATA = fp.read()
    IMAGE_404_CONTENT_TYPE = magic.from_buffer("image/png", mime=True)

    @staticmethod
    @lru_cache(maxsize=IMAGE_CACHE_SIZE)
    def load_image(bucket: str, object_name: str) -> Tuple[bytes, str]:
        file_object = create_default_minio_client().get_object(
            bucket,
            object_name,
        )
        content_type = file_object.headers.get("Content-Type")
        return file_object.data, content_type

    def get(self, request: Request, image_id: int):
        try:
            im: S3Image = S3Image.objects.get(id=image_id)
            data, content_type = self.load_image(
                im.bucket,
                im.object_name,
            )
            Event.objects.create(
                user=request.user,
                event_type="fetch_media",
                media_type="ImageList",
                data=json.dumps(dict(
                    id=image_id,
                ))
            )
            return HttpResponse(
                content=data,
                content_type=content_type or im.content_type
            )
        except S3Image.DoesNotExist:
            resp = HttpResponse(
                content=GetImageDataView.IMAGE_404_DATA,
                content_type=GetImageDataView.IMAGE_404_CONTENT_TYPE,
            )
            resp.status_code = status.HTTP_404_NOT_FOUND
            return resp


class GetVideoStream(APIView):
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)

    def get(self, request: Request, video_id: int):
        s3_video: S3Video = S3Video.objects.get(id=video_id)
        content_type, encoding = mimetypes.guess_type(s3_video.object_name)
        if content_type is None or not content_type.startswith("video"):
            content_type = "video/mp4"
        minio_client = get_default_minio_client()

        range_match = self.range_re.match(
            request.META.get('HTTP_RANGE', '').strip()
        )

        if range_match:
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte) if first_byte else 0
            last_byte = int(last_byte) if last_byte else minio_client.stat_object(
                s3_video.bucket,
                s3_video.object_name,
            ).size - 1
            length = last_byte - first_byte + 1

            obj = minio_client.get_object(
                s3_video.bucket,
                s3_video.object_name,
                offset=first_byte,
                length=length
            )
            content_length = obj.getheader('Content-Length')
            content_range = obj.getheader('Content-Range')

            Event.objects.create(
                user=request.user,
                event_type="fetch_media",
                media_type="VideoList",
                data=json.dumps(dict(
                    id=video_id,
                    content_length=content_length,
                    content_range=content_range,
                ))
            )

            def _wrapper():
                yield from obj.stream()
                obj.close()

            resp = StreamingHttpResponse(_wrapper(), status=206, content_type=content_type)
            resp['Content-Length'] = content_length
            resp['Content-Range'] = content_range
        else:
            obj = minio_client.get_object(
                s3_video.bucket,
                s3_video.object_name,
            )
            content_length = obj.getheader('Content-Length')

            def _wrapper():
                yield from obj.stream()
                obj.close()

            resp = StreamingHttpResponse(_wrapper(), content_type=content_type)
            resp['Content-Length'] = content_length
        resp['Accept-Ranges'] = 'bytes'
        return resp


class GetNovelPage(APIView):
    def get(self, request: Request, novel_id: int):
        novel: Novel = Novel.objects.get(id=novel_id)
        page_size = int(request.query_params.get("n", "4000"))
        page_id = int(request.query_params.get("p", "1"))
        page_count = ceil(novel.get_size() / page_size)
        if page_id > page_count or page_id <= 0:
            raise Exception(f"Can't reach that page {page_id}")

        text_decoded = novel.read_range(
            (page_id - 1) * page_size,
            page_id * page_size + 16
        ).decode(errors="ignore")
        Event.objects.create(
            user=request.user,
            event_type="fetch_media",
            media_type="Novel",
            data=json.dumps(dict(
                id=novel_id,
                page_size=page_size,
                page_id=page_id,
                page_count=page_count,
                character_count=len(text_decoded),
            ))
        )
        return Response({
            "text": text_decoded,
            "page_count": page_count
        })


class ExpandSearchByW2V(APIView):
    def get(self, request: Request):
        keywords = re.split(r"\s+", request.query_params.get("q") or "")
        similar_words = int(request.query_params.get("sw"))
        return Response({
            keyword: [
                {"word": w, "score": s}
                for w, s in title_expand(keyword, similar_words)
            ]
            for keyword in keywords
        })


class RecommendationRecord:
    def __init__(self, recommendation, expire: int = 3600 * 2):
        self.recommendation = recommendation
        self.expire = (datetime.datetime.now() + datetime.timedelta(seconds=expire)).timestamp()

    def is_expire(self):
        return datetime.datetime.now().timestamp() > self.expire


def get_model(user: User):
    model_path = os.path.join(RECSYS_MODEL_PATH, f"user_{user.id}.pt")
    try:
        log.info("Loading model from disk")
        with open(model_path, "rb") as fp:
            model_info = pickle.load(fp)
            if model_info["expire_timestamp"] > time.time():
                return model_info["model"]
            else:
                raise Exception("Model expired!")
    except Exception as ex:
        log.info("Falied to load model caused by:", exc_info=ex)
        model = train_model(user)
        with open(model_path, "wb") as fp:
            pickle.dump({
                "expire_timestamp": time.time() + 24 * 3600,
                "model": model
            }, fp)
        return model


recommendation_cache = dict()


def get_recommendations(user: User) -> List[int]:
    if user.id not in recommendation_cache or recommendation_cache[user.id].is_expire():
        log.info("Recommendation not found or expired, generating...")
        model = get_model(user)
        block_thread_ids = {
            tid for tid, tinfo in get_aggregated_logs(user).items()
            if tinfo.is_like is not None or tinfo.click_count > 1 or tinfo.impression_count > 3
        }
        candidates = list(ImageList.objects.all().values_list("title", "id"))
        scored_id = sorted(list(zip(
            [tid for _, tid in candidates],
            model.decision_function([title for title, _ in candidates])
        )), key=lambda x: -x[1])
        recommendation_cache[user.id] = RecommendationRecord(
            [tid for tid, _ in scored_id if tid not in block_thread_ids]
        )
    return recommendation_cache[user.id].recommendation


class RecommendImageList(APIView):
    def get(self, request: Request):
        recommendation = get_recommendations(request.user)
        page_size = int(request.query_params.get("n", "20"))
        page_id = int(request.query_params.get("p", "1"))
        page_recommendation = recommendation[(page_id - 1) * page_size:page_id * page_size]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(page_recommendation)])
        queryset = ImageList.objects.filter(pk__in=page_recommendation).order_by(preserved)
        serialized_data = ImageListSerializer(queryset, many=True).data
        # Rank again by RecSys model
        Event.objects.create(
            user=request.user,
            event_type="impression",
            media_type="ImageList",
            data=json.dumps(dict(
                page_size=page_size,
                page_id=page_id,
                source="recommendation",
                result=page_recommendation,
            ))
        )
        return Response(serialized_data)
