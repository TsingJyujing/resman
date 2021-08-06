import logging
import re
from typing import Iterable, List

from jieba import cut
from jieba import load_userdict
from jieba.analyse import ChineseAnalyzer
from jieba.analyse.analyzer import STOP_WORDS
from zhconv import convert

log = logging.getLogger(__file__)
load_userdict("nlp_resources/user_dict.txt")
try:
    with open("nlp_resources/stopwords.txt", "r") as fp:
        stop_words = frozenset(str(l).strip("\r\n") for l in fp.readlines())
except Exception as ex:
    log.error("Error while loading stopwords", exc_info=ex)
    stop_words = STOP_WORDS


def get_analyzer():
    return ChineseAnalyzer(stop_words)


FULL2HALF = str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})


def is_char_chinese(uchar):
    return u'\u4e00' <= uchar <= u'\u9fa5'


def is_str_all_chinese(data: str):
    return all(is_char_chinese(c) for c in data)


def clean_up_chinese_str(data: str):
    return convert(data.translate(FULL2HALF), 'zh-hans')


def text_clean_split(data: str) -> Iterable[List[str]]:
    buffer = []
    for s in re.split(r"\s+", clean_up_chinese_str(data)):
        for c in cut(s):
            buffer.append(c)
        if len(buffer) > 0:
            yield buffer
            buffer = []


def tokenizer(text: str) -> List[str]:
    buffer = []
    for s in re.split(r"\s+", clean_up_chinese_str(text)):
        for c in cut(s):
            buffer.append(c)
    return buffer
