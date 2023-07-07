#!/usr/bin/bash
# Need to provide STOPWORDS_URI, WORDVEC_URI, USER_DICT_URI
mkdir nlp_resources && cd nlp_resources && \
    wget https://nexus.tsingjyujing.com/repository/raw/nlp_resources/stopwords.txt && \
    wget https://nexus.tsingjyujing.com/repository/raw/nlp_resources/title.wordvectors && \
    wget https://nexus.tsingjyujing.com/repository/raw/nlp_resources/user_dict.txt && \
    cd /app
python manage.py migrate
gunicorn -c gunicorn_config.py resman.wsgi