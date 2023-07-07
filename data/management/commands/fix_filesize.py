from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from tqdm import tqdm
from whoosh import writing

from data.models import BaseS3Object, Novel, S3Image, S3Video


class Command(BaseCommand):
    help = "Fix file size"

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("type", help="s3image/s3video/novel")

    def handle(self, *args, **options):
        s3_class = {
            "s3image": S3Image,
            "s3video": S3Video,
            "novel": Novel,
        }["type"]
        s3_class = S3Image  # FIXME for type hint only
        s3_class.objects.filter()
