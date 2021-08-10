ARG PIP_INDEX_URL

FROM node:15 as BUILD_FRONTEND
ARG YARN_REGISTRY
WORKDIR /app
COPY frontend/yarn.lock frontend/package.json /app/
RUN yarn
COPY frontend/ .
RUN yarn build

FROM python:3.8 as CODE_CLEANER
WORKDIR /app
COPY . .
RUN rm -rf frontend

FROM python:3.8 as BACKEND
WORKDIR /app

CMD ["bash", "start_server.sh"]
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry &&  \
    poetry export --without-hashes -f requirements.txt -o requirements.txt &&  \
    mkdir nlp_resources && cd nlp_resources && \
    wget https://nexus.tsingjyujing.com/repository/raw/nlp_resources/stopwords.txt && \
    wget https://nexus.tsingjyujing.com/repository/raw/nlp_resources/title.wordvectors && \
    wget https://nexus.tsingjyujing.com/repository/raw/nlp_resources/user_dict.txt && \
    cd /app &&  \
    pip install -r requirements.txt

ENV DEV_MODE=0
COPY --from=CODE_CLEANER /app/ /app/
COPY --from=BUILD_FRONTEND /app/build/ /app/frontend/build/
