from abc import abstractmethod, ABC
from threading import Lock
from typing import Dict, Any

from rest_framework.viewsets import ModelViewSet
from whoosh.fields import Schema
from whoosh.filedb.filestore import FileStorage
from whoosh.index import Index

from resman.settings import WHOOSH_PATH


class WhooshSearchEngine:
    def __init__(self, path: str):
        self.storage = FileStorage(path)
        self.index_cache: Dict[str, Index] = dict()
        self.index_lock: Dict[str, Lock] = dict()
        self._get_lock_lock = Lock()

    def ensure_index(self, index: str, schema: Schema = None):
        self._get_index(index, schema)

    def _get_index(self, index: str, schema: Schema = None) -> Index:
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
        ix = self._get_index(index)
        with self._get_lock(index):
            w = ix.writer()
            w.update_document(**fields)
            w.commit()

    def insert_data(self, index: str, **fields):
        ix = self._get_index(index)
        with self._get_lock(index):
            w = ix.writer()
            w.add_document(**fields)
            w.commit()

    def delete_data(self, index: str, id_field, id_value):
        ix = self._get_index(index)
        with self._get_lock(index):
            w = ix.writer()
            w.delete_by_term(id_field, id_value)
            w.commit()


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
    def search_engine_delete(self, pk:str):
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
