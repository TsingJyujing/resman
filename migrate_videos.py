import json
import os

import pymongo
from bson.json_util import dumps
from tqdm import tqdm

from resman_client.client import ResmanClient, VideoList


def filename_to_index(filename: str):
    return int(filename.split("/")[-1].split(".")[0])


if __name__ == '__main__':
    mongo = pymongo.MongoClient("mongodb://dbadmin:979323846@172.30.0.74:27017")
    ic = ResmanClient("http://127.0.0.1:8000/", "resman", "resman_password")
    coll = mongo.get_database("website_pron").get_collection("video_info")

    for doc in tqdm(list(coll.find({"like": True, "migrated": {"$ne": True}}))):
        _id = doc["_id"]
        mp4_file = f"/mnt/Container/webserver/video/file/porv_{_id}.mp4"
        if os.path.isfile(mp4_file):
            video_list = ic.create_video_list(
                VideoList(
                    title=doc["name"],
                    description=" ".join(doc.get("tags", [])),
                    data=json.loads(dumps(doc))
                )
            )
            video_list.reaction = True
            video_list.upload_mp4_video(mp4_file)
        else:
            print(f"#{_id} skipped caused by no data")
        coll.update_one({"_id": _id}, {"$set": {"migrated": True}})
