import logging
from typing import List, Tuple

from gensim.models import KeyedVectors

log = logging.getLogger(__file__)
TITLE_MODEL = None


def title_expand(keyword: str, topn: int) -> List[Tuple[str, float]]:
    """
    Get top N similar words by keyword
    :param keyword:
    :return:
    """
    global TITLE_MODEL
    if TITLE_MODEL is None:
        log.info("Loading model for title word vectors")
        TITLE_MODEL = KeyedVectors.load_word2vec_format('nlp_resources/title.wordvectors', binary=False)
    if TITLE_MODEL is not None and keyword in TITLE_MODEL:
        return TITLE_MODEL.most_similar(positive=[keyword], topn=topn)
    else:
        return []
