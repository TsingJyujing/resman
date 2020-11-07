# noinspection PyBroadException
import json
import os
import traceback
from typing import BinaryIO
from resman.settings import DEBUG
from django.http import HttpResponse


class RangeFileWrapper(object):
    def __init__(self, file_like: BinaryIO, blksize: int = 8192, offset: int = 0, length: int = None):
        self._io = file_like
        self._io.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self._io, 'close'):
            self._io.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self._io.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self._io.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


# noinspection PyBroadException
def get_request_with_default(request, key, default_value):
    """
    Try to get value by specific key in request object, if can't find key in keySet, return default value.
    :param request: request object created by django
    :param key: key
    :param default_value: default value
    :return:
    """
    try:
        return request.GET[key]
    except:
        return default_value


def get_request_get(request, key):
    """
    Try to get value by specific key in request object, if can't find key in keySet, return None.
    :param request: request object created by django
    :param key: key
    :return:
    """
    return get_request_with_default(request, key, None)


def get_json_response(obj):
    """
    Create a http response
    :param obj: object which json serializable
    :return:
    """
    return HttpResponse(json.dumps(obj))


def get_host(request):
    """
    Get host info from request META
    :param request:
    :return:
    """
    return request.META["HTTP_HOST"].split(":")[0]


def response_json_error_info(func):
    """
    Trying to run function, if exception caught, return error details with json format
    :param func:
    :return:
    """

    def wrapper(request):
        try:
            return func(request)
        except Exception as ex:
            return get_json_response({
                "status": "error",
                "error_info": str(ex),
                "trace_back": traceback.format_exc()
            })

    return wrapper


def response_json(func):
    """
    Trying to run function, if exception caught, return error details with json format, else return json formatted object
    :param func:
    :return:
    """

    def wrapper(request):
        try:
            return get_json_response(func(request))
        except Exception as ex:
            return get_json_response({
                "status": "error",
                "error_info": str(ex),
                "trace_back": traceback.format_exc()
            })

    return wrapper


def debug_api(func):
    def wrapper(request):
        if DEBUG:
            return func(request)
        else:
            resp = get_json_response({
                "status": "error",
                "error_info": "Can't use debug api in non-debug mode."
            })
            resp.status_code = 404
            return resp
    return wrapper
