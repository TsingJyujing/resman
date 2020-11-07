import os

import pymongo

# ----------MONGO DB CONFIGURATION-----------

# Example: "mongodb://resman:123456@172.30.0.84:27017/?authSource=admin"
# FIXME use environment variable before commit
mongodb_uri = "mongodb://resman:123456@172.30.0.84:27017/?authSource=admin"  # os.environ["MONGODB_URI"]
mongodb_db_name = os.environ.get("MONGODB_DB", "resman")


def create_mongo_client():
    return pymongo.MongoClient(mongodb_uri)


mongodb_conn = create_mongo_client()


def get_collection(collection_name: str):
    return mongodb_conn.get_database(mongodb_db_name).get_collection(collection_name)


# ----------FILE PATH CONFIGURATION-----------

def ensure_created(dir_path: str):
    if os.path.isdir(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    return dir_path


media_root_path = "data"
video_buffer_path = ensure_created(os.path.join(media_root_path, "video/buffer"))
video_file_path = ensure_created(os.path.join(media_root_path, "video/file"))
video_preview_path = ensure_created(os.path.join(media_root_path, "video/preview"))
