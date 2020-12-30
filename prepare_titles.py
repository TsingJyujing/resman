import pymongo
from tqdm import tqdm

from utils.nlp.word_cut import text_clean_split


def get_texts():
    mongo = pymongo.MongoClient("mongodb://dbadmin:979323846@172.30.0.74:27017")

    coll = mongo.get_database("resman").get_collection("spider_sex8")
    for doc in tqdm(coll.find(), total=coll.count(), desc="sex8"):
        yield doc["title"]
        for c in doc["comments"]:
            yield c["content"]

    coll = mongo.get_database("website_pron").get_collection("novels")
    for doc in tqdm(coll.find(), total=coll.count(), desc="novels"):
        yield doc["title"]

    coll = mongo.get_database("website_pron").get_collection("images_info_ahash_weed")
    for doc in tqdm(coll.find(), total=coll.count(), desc="images"):
        yield doc["title"]


if __name__ == '__main__':
    with open("title_and_comments.txt", "w") as fp:
        for s in get_texts():
            for rs in text_clean_split(s):
                fp.write(" ".join(rs) + "\n")