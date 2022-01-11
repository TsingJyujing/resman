import logging
import pickle
from io import BytesIO
from typing import Iterator, Optional, Any
from urllib.parse import urlparse, unquote

from minio import Minio
from redis import Redis

from resman.settings import DEFAULT_S3_CONFIG, DEFAULT_S3_BUCKET, CACHE_REDIS_CONFIG

log = logging.getLogger(__file__)

redis_client = Redis.from_url(CACHE_REDIS_CONFIG) if CACHE_REDIS_CONFIG is not None else None


def redis_cache_get(key: str) -> Optional[Any]:
    if redis_client is not None:
        value = redis_client.get(key)
        if value is not None:
            return pickle.loads(value)
        else:
            return None
    else:
        return None


def redis_cache_set(key: str, value: Any):
    if redis_client is not None:
        redis_client.set(key, pickle.dumps(value))


def create_minio_client_from_config(s3_config: str) -> Minio:
    parse_result = urlparse(s3_config)
    return Minio(
        endpoint=(
            f"{parse_result.hostname}:{parse_result.port}"
            if parse_result.port is not None else parse_result.hostname
        ),
        access_key=unquote(parse_result.username),
        secret_key=unquote(parse_result.password),
        secure=parse_result.scheme == "https"
    )


def create_default_minio_client() -> Minio:
    return create_minio_client_from_config(DEFAULT_S3_CONFIG)


# Initialize default minio client
# Thread safe, but can't be shared between processes
DEFAULT_MINIO_CLIENT = None


def get_default_minio_client() -> Minio:
    global DEFAULT_MINIO_CLIENT
    if DEFAULT_MINIO_CLIENT is None:
        log.info("Initializing DEFAULT_MINIO_CLIENT")
        DEFAULT_MINIO_CLIENT = create_default_minio_client()
        if not DEFAULT_MINIO_CLIENT.bucket_exists(DEFAULT_S3_BUCKET):
            log.warning(f"Bucket {DEFAULT_S3_BUCKET} not existed, creating...")
            DEFAULT_MINIO_CLIENT.make_bucket(DEFAULT_S3_BUCKET)
    return DEFAULT_MINIO_CLIENT


def get_size(bucket_name: str, object_name: str) -> int:
    mc = get_default_minio_client()
    return mc.stat_object(bucket_name, object_name).size


def read_range_stream(bucket_name: str, object_name: str, start_byte: int = 0, end_byte: int = None) -> Iterator[bytes]:
    mc = get_default_minio_client()
    filesize = get_size(bucket_name, object_name)
    if end_byte is None:
        length = filesize
    else:
        length = end_byte - start_byte + 1
    obj = mc.get_object(
        bucket_name, object_name,
        offset=start_byte, length=length
    )
    yield from obj.stream()


def read_range(bucket_name: str, object_name: str, start_byte: int = 0, end_byte: int = None) -> bytes:
    with BytesIO() as fp:
        for ch in read_range_stream(bucket_name, object_name, start_byte, end_byte):
            fp.write(ch)
        fp.seek(0)
        return fp.read()
