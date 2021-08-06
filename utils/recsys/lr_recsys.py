import datetime
import json
import logging
from collections import defaultdict
from typing import Dict

import pandas
from django.contrib.auth.models import User
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from data.models import Event, ReactionToImageList, ImageList
from utils.nlp.word_cut import tokenizer

log = logging.getLogger(__file__)


class ThreadInfo:
    def __init__(self):
        self.impression_count = 0
        self.click_count = 0
        self.is_like = None


def get_aggregated_logs(user: User, training_data_days: int = 180) -> Dict[int, ThreadInfo]:
    start_date = datetime.datetime.now() - datetime.timedelta(days=training_data_days)
    result_map = defaultdict(ThreadInfo)
    for impression_event in Event.objects.filter(
            event_type="impression",
            media_type="ImageList",
            user=user,
            created__gt=start_date,
    ):
        for tid in json.loads(impression_event.data)["result"]:
            result_map[int(tid)].impression_count += 1
    for click_event in Event.objects.filter(
            event_type="page_view",
            media_type="ImageList",
            user=user,
            created__gt=start_date,
    ):
        result_map[int(json.loads(click_event.data)["id"])].click_count += 1
    for reaction in ReactionToImageList.objects.filter(
            owner=user
    ):
        result_map[int(reaction.thread.id)].is_like = reaction.positive_reaction
    return result_map


def collect_imagelist_training_data(user: User, training_data_days: int = 180) -> pandas.DataFrame:
    rows = []
    for thread_id, record in get_aggregated_logs(user, training_data_days).items():
        try:
            il = ImageList.objects.get(id=thread_id)
            rows.append(dict(
                thread_id=thread_id,
                title=il.title,
                y=record.is_like is True or record.click_count > 2
            ))
        except ImageList.DoesNotExist:
            pass
    return pandas.DataFrame(rows)


def train_model(user: User, training_data_days: int = 180, lr_C: float = 4.0):
    vectorizor = CountVectorizer(
        analyzer=tokenizer,
        lowercase=False,
        max_df=0.95,
        min_df=3,
    ).fit([x["title"] for x in ImageList.objects.all().values("title")])
    df = collect_imagelist_training_data(user, training_data_days)
    X_train, X_test, y_train, y_test = train_test_split(
        vectorizor.transform(df["title"].tolist()),
        df["y"].to_numpy(),
        test_size=0.15,
        random_state=0
    )
    lr_model = LogisticRegression(
        C=lr_C,
        penalty='l1',
        solver='liblinear',
        class_weight="balanced",
        max_iter=1000,
        verbose=True
    )
    lr_model.fit(X_train, y_train)
    test_roc = roc_auc_score(y_test, lr_model.decision_function(X_test))
    train_roc = roc_auc_score(y_train, lr_model.decision_function(X_train))
    log.info(f"New model trained for user {user} Test AUC(ROC)={test_roc} Train AUC(ROC)={train_roc}")
    return Pipeline([
        ("str2vec", vectorizor),
        ("scoring", lr_model)
    ])
