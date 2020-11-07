# Create your views here.
import json
import logging
import math
import mimetypes
import os
import re
import shutil
from wsgiref.util import FileWrapper

import numpy
from PIL import Image
from bson import ObjectId
from django.http import HttpRequest
from django.http.response import StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from moviepy.video.VideoClip import VideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from utils.config import get_collection, video_file_path, video_buffer_path, video_preview_path
from utils.http import RangeFileWrapper, response_json
from utils.verifier import verify_json_fields

log = logging.getLogger(__file__)
range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)


def calc_image_size(w: int, h: int, w_lim: int, h_lim: int):
    if w < w_lim and h < h_lim:
        return w, h
    ratio = min(w_lim * 1.0 / w, h_lim * 1.0 / h)
    return int(round(ratio * w)), int(round(ratio * h))


# FIXME @login_required

@require_http_methods(["PUT"])
@response_json
def upload_video(request: HttpRequest):
    """
    Upload video to server
    :param request:
    :return:
    """
    video_info: dict = json.loads(request.body.decode())
    verify_json_fields(video_info, dict(
        title=str,  # title of the video
        source=str,  # Source of the video, to unique in spider
    ))
    # Fill other field
    if "_id" in video_info:
        video_info.pop("_id")
        log.warning("Field _id in video info, removed")

    if "tags" not in video_info:
        video_info["tags"] = []

    video_info["like"] = False

    temp_id = str(ObjectId())
    temp_file_path = os.path.join(video_buffer_path, f"{temp_id}.mp4")
    temp_preview_path = os.path.join(video_buffer_path, f"{temp_id}.gif")
    f = request.FILES['file']
    with open(temp_file_path, "wb") as fp:
        for chunk in f.chunks():
            fp.write(chunk)

    video_cap = VideoFileClip(temp_file_path)
    frame_size = video_cap.size

    video_info["fps"] = video_cap.fps
    video_info["duration"] = video_cap.duration
    video_info["width"], video_info["height"] = frame_size[0], frame_size[1]

    im_w, im_h = calc_image_size(frame_size[0], frame_size[1], 640, 480)
    img_count = 15
    duration = 0.5

    def make_frame(t):
        arr = video_cap.get_frame((video_cap.duration - 3) * t / (img_count * duration))
        return numpy.array(
            Image.fromarray(arr).resize((im_w, im_h))
        )

    vc = VideoClip(
        make_frame=make_frame,
        duration=img_count * duration
    ).set_fps(
        math.ceil(1 / duration)
    )
    vc.write_gif(temp_preview_path)

    del vc
    del video_cap

    _id: ObjectId = get_collection("videos").insert_one(video_info).inserted_id
    shutil.move(temp_file_path, os.path.join(video_file_path, str(_id)))
    shutil.move(temp_preview_path, os.path.join(video_preview_path, str(_id)))

    return {"status": "success"}


# TODO API get video ID list by source str

# TODO API to modify video meta

# TODO API to delete video

# TODO API search and get video list

# TODO API get preview file

# FIXME need login
def stream_video(request: HttpRequest, video_id: str):
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    # FIXME Modify path by video ID
    print(f"Get video ID {video_id}")
    path = "data/test.mp4"
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(
            RangeFileWrapper(
                open(path, 'rb'),
                offset=first_byte,
                length=length
            ),
            status=206,
            content_type=content_type
        )
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp
