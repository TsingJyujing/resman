from io import BytesIO
from typing import Optional, Union, BinaryIO

import magic

from resman_client.base import BaseClient


class ImageThreadClient(BaseClient):
    def __init__(self, endpoint: str, user: str, password: str, image_thread_id: int):
        super().__init__(endpoint, user, password)
        self.image_thread_id = image_thread_id

    @property
    def reaction(self) -> Optional[bool]:
        resp = self.get(
            f"api/image_thread/{self.image_thread_id}/reaction"
        )
        resp.raise_for_status()
        return resp.json()["positive_reaction"]

    @reaction.setter
    def reaction(self, positive_reaction: Optional[bool]):
        resp = self.post(
            f"api/image_thread/{self.image_thread_id}/reaction",
            json=dict(
                positive_reaction=positive_reaction
            )
        )
        resp.raise_for_status()

    @property
    def data(self):
        resp = self.get(f"api/image_thread/{self.image_thread_id}")
        resp.raise_for_status()
        return resp.json()

    def destroy(self):
        self.delete(f"api/image_thread/{self.image_thread_id}").raise_for_status()

    def append_s3_image(self, bucket: str, object_name: str, order: int = 0):
        self.post(
            f"api/image/upload",
            json=dict(
                image_thread_id=self.image_thread_id,
                bucket=bucket,
                object_name=object_name,
                order=order,
            )
        ).raise_for_status()

    def upload_image(self, file: Union[bytes, str, BinaryIO], order: int = 0):
        if isinstance(file, str):
            with open(file, "rb") as fp:
                data = fp.read()
        elif isinstance(file, bytes):
            data = file
        else:
            data = file.read()
        mime = magic.from_buffer(data, mime=True)
        self.post(
            f"api/image/upload",
            data=dict(
                image_thread_id=self.image_thread_id,
                order=order,
            ),
            files=dict(file=("data", BytesIO(data), mime))
        ).raise_for_status()


class ImageClient(BaseClient):
    def __init__(self, endpoint: str, user: str, password: str):
        super().__init__(endpoint, user, password)

    def get_image_thread(self, image_thread_id: int):
        return ImageThreadClient(
            self._endpoint,
            self._user,
            self._password,
            image_thread_id=image_thread_id
        )

    def create_image_thread(self, title: str, description: str, data: dict):
        resp = self.post(
            "api/image_thread",
            json=dict(
                title=title,
                description=description,
                data=data,
            )
        )
        resp.raise_for_status()
        return self.get_image_thread(int(resp.json()["id"]))
