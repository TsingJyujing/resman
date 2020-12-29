import json
import os
import random

from resman_client.image import ImageClient

if __name__ == '__main__':
    image_thread = ImageClient("http://127.0.0.1:8000/", "resman", "resman_password").create_image_thread(
        "Test Thread", "Test Thread", {
            "author": "Tsing Jyujing",
            "source_url": "http://abc.com"
        }
    )
    print(json.dumps(
        image_thread.data,
        indent=2
    ))
    data_dir = "statics/image/test"
    image_thread.upload_images([
        os.path.join(data_dir, f)
        for i, f in enumerate(random.sample(os.listdir(data_dir), k=10))
    ], 0)
    # image_thread.append_s3_image("spider", "uxxx.jpeg", 10)
    last_status = None
    operation_seq = [random.choice([True, False, None]) for _ in range(5)]
    for s in operation_seq:
        print(f"Modifying {last_status}->{s}")
        image_thread.reaction = s
        assert image_thread.reaction == s
        last_status = s
    image_thread.reaction = True
    # image_thread.destroy()
