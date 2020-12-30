import re
from abc import abstractmethod, ABC
from threading import Lock
from typing import Dict, Any, List

from rest_framework.viewsets import ModelViewSet
from whoosh.fields import Schema
from whoosh.filedb.filestore import FileStorage
from whoosh.index import Index
from whoosh.query import Term, Query
from whoosh.query.compound import DisjunctionMax, AndMaybe

from resman.settings import WHOOSH_PATH
from utils.nlp.w2v_search import title_expand
from utils.nlp.word_cut import text_clean_split


class WhooshSearchEngine:
    def __init__(self, path: str):
        self.storage = FileStorage(path)
        self.index_cache: Dict[str, Index] = dict()
        self.index_lock: Dict[str, Lock] = dict()
        self._get_lock_lock = Lock()

    def ensure_index(self, index: str, schema: Schema = None):
        self.get_index(index, schema)

    def get_searcher(self, index: str):
        if not self.storage.index_exists(index):
            raise Exception("Index not existed")
        return self.get_index(index).searcher()

    def get_index(self, index: str, schema: Schema = None) -> Index:
        """
        Get index only for read operation
        :param index:
        :param schema:
        :return:
        """
        if index not in self.index_cache:
            if self.storage.index_exists(index):
                self.index_cache[index] = self.storage.open_index(index)
            else:
                self.index_cache[index] = self.storage.create_index(schema, indexname=index)
        return self.index_cache[index]

    def _get_lock(self, index: str):
        with self._get_lock_lock:
            if index not in self.index_lock:
                self.index_lock[index] = Lock()
            return self.index_lock[index]

    def update_data(self, index: str, **fields):
        ix = self.get_index(index)
        with self._get_lock(index):
            with ix.writer() as w:
                w.update_document(**fields)

    def insert_data(self, index: str, **fields):
        ix = self.get_index(index)
        with self._get_lock(index):
            with ix.writer() as w:
                w.add_document(**fields)

    def delete_data(self, index: str, id_field, id_value):
        ix = self.get_index(index)
        with self._get_lock(index):
            with ix.writer() as w:
                w.delete_by_term(id_field, id_value)


WHOOSH_SEARCH_ENGINE = WhooshSearchEngine(WHOOSH_PATH)


class ISearchable:
    """
    For implementation of model view set
    """

    @classmethod
    @abstractmethod
    def get_schema(cls) -> Schema: pass

    @classmethod
    @abstractmethod
    def get_index_name(cls) -> str: pass

    @abstractmethod
    def to_fields(self) -> Dict[str, Any]: pass


class SearchableModelViewSet(ModelViewSet):

    @abstractmethod
    def search_engine_create(self, instance: ISearchable):
        """
        Sync on object to elasticsearch
        :param instance: The model to create/delete/
        :return:
        """
        pass

    @abstractmethod
    def search_engine_update(self, instance: ISearchable):
        """
        Sync on object to elasticsearch
        :param instance: The model to create/delete/
        :return:
        """
        pass

    @abstractmethod
    def search_engine_delete(self, pk: str):
        """
        :param pk:
        :return:
        """
        pass

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        self.search_engine_create(serializer.instance)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self.search_engine_delete(pk=self.get_object().id)
        return response

    def update(self, request, *args, **kwargs):
        self.search_engine_update(self.get_object())
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.search_engine_update(self.get_object())
        return super().partial_update(request, *args, **kwargs)


class WhooshSearchableModelViewSet(SearchableModelViewSet, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        WHOOSH_SEARCH_ENGINE.ensure_index(
            self.get_index_name(),
            self.get_schema()
        )

    @abstractmethod
    def get_index_name(self) -> str: pass

    @abstractmethod
    def get_schema(self) -> Schema: pass

    def search_engine_create(self, instance: ISearchable):
        WHOOSH_SEARCH_ENGINE.insert_data(self.get_index_name(), **instance.to_fields())

    def search_engine_update(self, instance: ISearchable):
        WHOOSH_SEARCH_ENGINE.update_data(self.get_index_name(), **instance.to_fields())

    def search_engine_delete(self, pk: str):
        WHOOSH_SEARCH_ENGINE.delete_data(self.get_index_name(), "id", pk)

    def get_searcher(self):
        return WHOOSH_SEARCH_ENGINE.get_searcher(self.get_index_name())


def parse_title_query(fieldname: str, query_info: str, n_expand: int):
    def get_term(text: str, boost: float = 1.0):
        return Term(fieldname, text, boost)

    def connect_and_maybe(queries: List[Query]):
        term_size = len(queries)
        if term_size == 1:
            return queries[0]
        elif term_size == 2:
            return AndMaybe(queries[0], queries[1])
        else:
            return AndMaybe(queries[0], connect_and_maybe(queries[1:]))

    def cut_result():
        for ws in re.split(r"\s+", query_info):
            for rs in text_clean_split(ws):
                yield from rs

    query_list = []
    for w in cut_result():
        term_list = [get_term(w)]
        term_list += [get_term(s, v * 0.5) for s, v in title_expand(w, n_expand)]
        query_list.append(DisjunctionMax(term_list))

    return connect_and_maybe(query_list)
