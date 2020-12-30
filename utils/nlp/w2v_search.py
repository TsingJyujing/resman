import logging
from typing import List, Tuple

from gensim.models import KeyedVectors

log = logging.getLogger(__file__)
TITLE_MODEL = None
try:
    TITLE_MODEL = KeyedVectors.load_word2vec_format('nlp_resources/title.wordvectors', binary=False)
except Exception as ex:
    log.error("Error while loading title word2vec model", exc_info=ex)


def title_expand(keyword: str, topn: int) -> List[Tuple[str, float]]:
    """
    Get top N similar words by keyword
    :param keyword:
    :return:
    """
    if TITLE_MODEL is not None and keyword in TITLE_MODEL:
        return TITLE_MODEL.most_similar(positive=[keyword], topn=topn)
    else:
        return []
