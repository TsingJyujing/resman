from io import BytesIO
from typing import Optional, Union, BinaryIO, List

import magic
from pydantic import BaseModel

from resman_client.base import BaseClient


class DefaultS3Image(BaseModel):
    bucket: str
    object_name: str
    order: int


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

    def append_s3_images(self, images: List[DefaultS3Image]):
        self.post(
            f"api/image/upload",
            json=dict(
                image_thread_id=self.image_thread_id,
                default_s3_files=[
                    m.dict()
                    for m in images
                ]
            )
        ).raise_for_status()

    def upload_images(self, files: List[Union[bytes, str, BinaryIO]], order: int = 0):
        files_commit = {}
        for i, file in enumerate(files):
            if isinstance(file, str):
                with open(file, "rb") as fp:
                    data = fp.read()
            elif isinstance(file, bytes):
                data = file
            else:
                data = file.read()
            mime = magic.from_buffer(data, mime=True)
            files_commit[f"file_{i + order}"] = (str(i + order), BytesIO(data), mime)
        self.post(
            f"api/image/upload",
            data=dict(image_thread_id=self.image_thread_id),
            files=files_commit
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
