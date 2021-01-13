import logging
from urllib.parse import urlparse, unquote

from minio import Minio

from resman.settings import DEFAULT_S3_CONFIG, DEFAULT_S3_BUCKET

log = logging.getLogger(__file__)


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
