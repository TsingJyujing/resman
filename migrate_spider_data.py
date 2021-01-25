import json
from mimetypes import guess_type

import pymongo
from bson.json_util import dumps
from tqdm import tqdm

from resman_client.client import ResmanClient, DefaultS3Image, ImageList
from utils.storage import create_minio_client_from_config


def filename_to_index(filename: str):
    return int(filename.split("/")[-1].split(".")[0])


if __name__ == '__main__':
    mongo = pymongo.MongoClient("mongodb://dbadmin:979323846@172.30.0.74:27017")
    mc = create_minio_client_from_config("http://tsingjyujing:979323846@172.30.0.74:8333/")
    ic = ResmanClient("http://127.0.0.1:8000/", "resman", "resman_password")
    coll = mongo.get_database("resman").get_collection("spider_sex8")
    for doc in tqdm(list(coll.find({"migrated": {"$ne": True}}))):
        _id = doc["_id"]
        image_list = []
        for obj in mc.list_objects("spider", f"sex8/{str(_id)}/images/"):
            content_type = guess_type(obj.object_name)[0]
            if content_type is not None and content_type.startswith("image"):
                image_list.append(DefaultS3Image(
                    bucket="spider",
                    object_name=obj.object_name,
                    order=filename_to_index(obj.object_name)
                ))
        if len(image_list) > 0:
            ic.create_image_list(
                ImageList(
                    title=doc["title"],
                    description=doc["subject"]["content"],
                    data=json.loads(dumps(doc))
                )
            ).append_s3_images(image_list)
        coll.update_one({"_id": _id}, {"$set": {"migrated": True}})
