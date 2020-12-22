import logging
import os
from multiprocessing import Manager, Process
from queue import Empty
from threading import Thread
from typing import List

from utils.ml.word2vec import read_file, text_clean_split

log = logging.getLogger(__file__)

manager = Manager()
result_queue = manager.Queue()
task_queue = manager.Queue()


def process_process():
    while True:
        try:
            fn = task_queue.get(block=False)
            for line in read_file(fn):
                result_queue.put(list(text_clean_split(line)))
        except Empty:
            break


def main(corpus_dir: str, result_file: str):
    log.info("Reading file list...")
    for fn in (os.path.join(corpus_dir, f) for f in os.listdir(corpus_dir) if f.endswith(".txt")):
        task_queue.put(fn)

    def save_data():
        with open(result_file, "w") as fp:
            while True:
                r = result_queue.get(block=True)
                if isinstance(r, List):
                    for rs in r:
                        fp.write(" ".join(rs))
                        fp.write("\n")
                elif isinstance(r, str):
                    if r == "DONE":
                        log.info("DONE received")
                        break
                else:
                    raise Exception(f"Can't process {type(r)} data: {repr(r)[:100]}")

    log.info("Starting saving thread")
    saving_thread = Thread(target=save_data)
    saving_thread.start()

    log.info("Starting process pool")

    ps = [Process(target=process_process) for _ in range(11)]
    for p in ps:
        p.start()
    for p in ps:
        p.join()

    result_queue.put("DONE")
    saving_thread.join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main("/mnt/Container/webserver/novel", "dev/data/corpus.txt")
