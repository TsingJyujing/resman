import json

import pymongo
from bson.json_util import dumps
from tqdm import tqdm

from resman_client.image import ImageClient, DefaultS3Image

from utils.storage import create_minio_client_from_config


def filename_to_index(filename: str):
    return int(filename.split("/")[-1].split(".")[0])


if __name__ == '__main__':
    mongo = pymongo.MongoClient("mongodb://dbadmin:979323846@172.30.0.74:27017")
    mc = create_minio_client_from_config("http://tsingjyujing:979323846@172.30.0.74:8333/")
    ic = ImageClient("http://127.0.0.1:8000/", "resman", "resman_password")
    coll = mongo.get_database("resman").get_collection("spider_sex8")
    for doc in tqdm(list(coll.find().sort("_id", direction=pymongo.DESCENDING))):
        ic.create_image_thread(
            title=doc["title"],
            description=doc["subject"]["content"],
            data=json.loads(dumps(doc))
        ).append_s3_images([
            DefaultS3Image(
                bucket="spider",
                object_name=obj.object_name,
                order=i
            )
            for i, obj in enumerate(sorted(
                list(mc.list_objects("spider", f"sex8/{str(doc['_id'])}/images/")),
                key=lambda o: filename_to_index(o.object_name)
            ))
        ])
