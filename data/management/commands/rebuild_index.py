from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from tqdm import tqdm
from whoosh import writing

from data.models import ImageList, Novel, VideoList
from utils.search_engine import WHOOSH_SEARCH_ENGINE


class Command(BaseCommand):
    help = "Rebuild Whoosh Index"

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("index_type", help="videolist/imagelist/novel")

    def handle(self, *args, **options):
        index_type = options["index_type"]
        search_engine = WHOOSH_SEARCH_ENGINE

        if index_type == "imagelist":
            model_class = ImageList
        elif index_type == "videolist":
            model_class = VideoList
        elif index_type == "novel":
            model_class = Novel
        else:
            raise Exception(f"Do not support {index_type} yet")
        index = search_engine.get_index(
            model_class.get_index_name(), model_class.get_schema()
        )
        with index.writer() as w:
            w.mergetype = writing.CLEAR
        with index.writer() as w:
            for il in tqdm(model_class.objects.all()):
                w.add_document(**il.to_fields())
