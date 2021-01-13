import logging
from datetime import datetime
from mimetypes import guess_type

import pandas
import pymongo
from bson.json_util import dumps
from django.contrib.auth.models import User
from tqdm import tqdm

from data.models import ImageThread, DefaultS3Image
from utils.search_engine import WHOOSH_SEARCH_ENGINE
from utils.storage import create_minio_client_from_config

log = logging.getLogger("Create Test Super User")
logging.basicConfig(
    level=logging.DEBUG
)


def filename_to_index(filename: str):
    return int(filename.split("/")[-1].split(".")[0])


def to_datetime(tick: str):
    try:
        return pandas.to_datetime(tick)
    except:
        log.info(f"Can't parse {tick}, using now")
        return datetime.now()


def migrate():
    mongo = pymongo.MongoClient("mongodb://dbadmin:979323846@172.30.0.74:27017")
    mc = create_minio_client_from_config("http://tsingjyujing:979323846@172.30.0.74:8333/")
    coll = mongo.get_database("resman").get_collection("spider_sex8")
    user = User.objects.first()

    WHOOSH_SEARCH_ENGINE.ensure_index(ImageThread.get_index_name(), ImageThread.get_schema())

    for doc in tqdm(list(coll.find())):
        image_thread: ImageThread = ImageThread.objects.create(
            title=doc["title"],
            description=doc["subject"]["content"],
            data=dumps(doc),
            owner=user,
            # created=to_datetime(doc["subject"]["tick"]),
            # updated=to_datetime(doc["subject"]["tick"])
        )
        WHOOSH_SEARCH_ENGINE.insert_data(image_thread.get_index_name(), **image_thread.to_fields())
        for obj in mc.list_objects("spider", f"sex8/{str(doc['_id'])}/images/"):
            content_type = guess_type(obj.object_name)[0]
            if content_type is not None and content_type.startswith("image"):
                i = filename_to_index(obj.object_name)
                DefaultS3Image.objects.create(
                    bucket="spider",
                    object_name=obj.object_name,
                    order=i,
                    thread=image_thread,
                    content_type=content_type
                )
            else:
                log.info(f"Skip file {obj.object_name}")
