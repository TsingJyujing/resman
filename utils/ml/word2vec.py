"""
Using word2vec to train embedding on Chinese corpus
"""
import json

from zhconv import convert
import chardet
import logging
from typing import Iterable, List, Tuple
from jieba import cut

log = logging.getLogger(__file__)


def is_char_chinese(uchar):
    return u'\u4e00' <= uchar <= u'\u9fa5'


def is_str_all_chinese(data: str):
    return all(is_char_chinese(c) for c in data)


def read_file(filepath: str) -> Iterable[str]:
    with open(filepath, "rb") as fp:
        encoding_info = chardet.detect(fp.read())
    if "encoding" in encoding_info and encoding_info.get("confidence", 0) > 0.9:
        encoding = encoding_info["encoding"]
        log.debug(f"Reading {filepath} with encoding={encoding}")
        with open(filepath, "r", encoding=encoding) as fp:
            yield from fp.readlines()
    else:
        log.warning(f"File {filepath} skipped caused by encoding info is fuzzy: {json.dumps(encoding_info)}")


FULL2HALF = str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})


def text_clean_split(data: str) -> Iterable[List[str]]:
    buffer = []
    for s in cut(convert(data.translate(FULL2HALF), 'zh-hans')):
        if is_str_all_chinese(s):
            buffer.append(s)
        elif s in {"!", "?", ";", "。", "！", "？", "；"}:  # Stop sentence
            yield buffer
            buffer = []
    if len(buffer) > 0:
        yield buffer


