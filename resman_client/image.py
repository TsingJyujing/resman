from resman_client.base import BaseClient


class ImageClient(BaseClient):
    def __init__(self, endpoint: str, user: str, password: str):
        super().__init__(endpoint, user, password)

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
        return resp.json()
