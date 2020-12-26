from resman_client.image import ImageClient

if __name__ == '__main__':
    print(
        ImageClient("http://127.0.0.1:8000/", "resman", "resman_password").create_image_thread(
            "Test Thread", "Test Thread", {
                "author": "Tsing Jyujing",
                "source_url": "http://abc.com"
            }
        )
    )
