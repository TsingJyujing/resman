# ResMan Client

## Introduction

This is the client of [Resman Server](https://github.com/TsingJyujing/resman).

Use `pip install resman-client` to install it.

## Initialize

```python
from resman_client import ResmanClient

client = ResmanClient(
    "https://resman.xxx.com/",
    "user-name",
    "password"
)
```

## Image List

```python
from resman_client import ImageList, DefaultS3Image, ImageListClient

image_list: ImageListClient = client.create_image_list(
    ImageList(
        title="title",
        description="content",
        data={
            # jsonable object
        }
    )
)

image_list.append_s3_images([
    # DefaultS3Image objects
    # Can be different bucket, but must be same server as Resman Server
])

image_list.upload_images([
    # filenames, binary data or binary IOs
])
```

## Video List

```python
from resman_client import VideoListClient, VideoList

video_list: VideoListClient = client.create_video_list(
    VideoList(
        title="title",
        description="whatever",
        data={
            # jsonable object 
        }
    )
)

# Upload video
video_list.upload_mp4_video(
    "mp4 file path"
)
```

## Novel

```python
from resman_client import NovelClient, Novel

novel: NovelClient = client.create_novel(
    Novel(
        title="title",
        data={
            # jsonable object 
        }
    ),
    text="Content of the novel"
)
```


## Some Notice

- Support mp4 (h264/h265) video only
- data is a JSON body to store some metadata like original URL, won't be displayed in website
- Video and Image list have an attribute order to control the order, auto increasing (+1) will be applied while uploading multi objects, the order of objects with same `order` field can't be predicted.