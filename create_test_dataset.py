import json
import os
import random

from resman_client.client import ResmanClient, ImageList, Novel, VideoList


def create_imagelist(resman_client: ResmanClient):
    image_list_info = ImageList(
        title="Test Thread",
        description="Test Thread Description",
        data={
            "author": "Tsing Jyujing",
            "source_url": "http://abc.com"
        }
    )
    image_list = resman_client.create_image_list(image_list_info)
    print(json.dumps(image_list.data, indent=2))

    data_dir = "test_data/image"
    image_list.upload_images(list(
        os.path.join(data_dir, f)
        for i, f in enumerate(random.sample(os.listdir(data_dir), k=10))
    ), 0)

    last_status = None
    operation_seq = [random.choice([True, False, None]) for _ in range(5)]
    for s in operation_seq:
        print(f"Modifying {last_status}->{s}")
        image_list.reaction = s
        assert image_list.reaction == s
        last_status = s
    image_list.reaction = True


def create_novel(resman_client: ResmanClient):
    data_dir = "test_data/novel"
    for file in os.listdir(data_dir):
        title = "".join(file.split(".")[:-1])
        with open(os.path.join(data_dir, file)) as fp:
            novel_info = Novel(
                title=title,
                data={
                    "filename": file
                }
            )
            novel = resman_client.create_novel(novel_info, fp.read())
        print("Novel created: {}".format(json.dumps(novel.data, indent=2)))


def create_video(resman_client: ResmanClient):
    data_dir = "test_data/video"
    for mp4_file in os.listdir(data_dir):
        with open(os.path.join(data_dir, mp4_file), "rb") as fp:
            video_list = resman_client.create_video_list(VideoList(
                title=mp4_file,
                description="test file",
                data={}
            ))
            print(f"Video List: {json.dumps(video_list.data, indent=2)}, uploading.")
            video_list.upload_h264_video(fp, order=0)
            print("Uploaded.")


if __name__ == '__main__':
    rc = ResmanClient("http://127.0.0.1:8000/", "resman", "resman_password")
    create_novel(rc)
    create_video(rc)
    create_imagelist(rc)