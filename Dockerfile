ARG PIP_INDEX_URL

FROM node:15 as BUILD_FRONTEND
ARG YARN_REGISTRY
WORKDIR /app
COPY frontend/yarn.lock frontend/package.json /app/
RUN yarn
COPY frontend/ .
RUN yarn build

FROM python:3.8 as POETRY_EXPORT
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock /app/
RUN poetry export --without-hashes -f requirements.txt -o requirements.txt

FROM python:3.8 as CODE_CLEANER
WORKDIR /app
COPY . .
RUN rm -rf frontend

FROM python:3.8 as BACKEND
WORKDIR /app

CMD ["bash", "start_server.sh"]
RUN mkdir nlp_resources && cd nlp_resources && \
    wget https://nexus.tsingjyujing.com/repository/raw/nlp_resources/stopwords.txt && \
    wget https://nexus.tsingjyujing.com/repository/raw/nlp_resources/title.wordvectors && \
    wget https://nexus.tsingjyujing.com/repository/raw/nlp_resources/user_dict.txt && \
    cd /app
COPY --from=POETRY_EXPORT /app/requirements.txt /app/
RUN pip install -r requirements.txt
ENV DEV_MODE=0
COPY --from=CODE_CLEANER /app/ /app/
COPY --from=BUILD_FRONTEND /app/build/ /app/frontend/build/
