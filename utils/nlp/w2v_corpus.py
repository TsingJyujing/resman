"""
Using word2vec to train embedding on Chinese corpus
"""
import json
import logging
import os
from multiprocessing import Pool
from typing import Iterable
import chardet

from utils.nlp.word_cut import text_clean_split

log = logging.getLogger(__file__)


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


def process_single_file(p):
    try:
        src, dst = p
        with open(dst, "w") as fp:
            for line in read_file(src):
                for rs in text_clean_split(line):
                    fp.write(" ".join(rs))
                    fp.write("\n")
        return True
    except Exception as ex:
        log.error(f"Error while executing task: {p}", exc_info=ex)
        return False


def convert_all_text_files(corpus_dir: str, result_dir: str):
    """
    Convert all text file in corpus dir to result dir
    :param corpus_dir:
    :param result_dir:
    :return:
    """
    log.info("Reading file list...")
    files = [
        (
            os.path.join(corpus_dir, f),
            os.path.join(result_dir, f),
        )
        for f in os.listdir(corpus_dir)
        if f.endswith(".txt")
    ]
    with Pool() as p:
        results = p.map(process_single_file, files)
    assert all(results), "Failed in some file"
