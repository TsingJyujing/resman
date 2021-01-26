import json

import pymongo
from bson.json_util import dumps
from tqdm import tqdm

from resman_client.client import ResmanClient, Novel
from utils.nlp.w2v_corpus import read_file


def filename_to_index(filename: str):
    return int(filename.split("/")[-1].split(".")[0])


if __name__ == '__main__':
    mongo = pymongo.MongoClient("mongodb://dbadmin:979323846@172.30.0.74:27017")

    ic = ResmanClient("http://127.0.0.1:8000/", "resman", "resman_password")
    coll = mongo.get_database("website_pron").get_collection("novels")

    for doc in tqdm(list(coll.find({"migrated": {"$ne": True}}))):
        _id = doc["_id"]
        data = list(read_file(f"/mnt/Container/webserver/novel/{_id}.txt"))
        if len(data) > 0:
            novel = ic.create_novel(
                Novel(
                    title=doc["title"],
                    data=json.loads(dumps(doc))
                ),
                text="\n".join(data)
            )
            if doc.get("like", False):
                novel.reaction = True
        else:
            print(f"#{_id} skipped caused by no data")
        coll.update_one({"_id": _id}, {"$set": {"migrated": True}})
