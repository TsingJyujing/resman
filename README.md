# ResMan

一个开源的资源管理网站/An open-sources resource management website.

(This project mainly wrote in English (UI/Commend/...) but NLP part is Chinese only, feel free to give me some suggestions to support English)


## Quick Start

### Using SQLite

Using SQLite is the fastest way to start the server, only need to start 1 container and only requires around 200~300M memory.

```yaml
version: "3"
services:
  api:
    image: "tsingjyujing/resman:latest"
    restart: always
    ports:
      - "8000:8000"
    environment:
      USING_DB: sqlite3
      SQLITE3_CONFIG: /data/db.sqlite3
      WHOOSH_PATH: /data/whoosh_index
      S3_CONFIG: https://<access_key>:<secret_key>@<s3_host>:<s3_port>/
      S3_BUCKET: resman
      IMAGE_CACHE_SIZE: 3 # Set value by your memory
    command: ["python", "manage.py", "runserver", "--noreload", "0.0.0.0:8000"]
    volumes:
      - <Your Data Path>:/data
```

### Using PostgreSQL

```yaml
version: "3"
services:
  db:
    image: "postgres"
    restart: always 
    environment:
      POSTGRES_USER: resman
      POSTGRES_PASSWORD: <db password>
      PGDATA: "/data"
    volumes:
      - "<Your Database Data Path>:/data"
  api:
    image: "tsingjyujing/resman:latest"
    restart: always
    depends_on:
      - "db"
    ports:
      - "8000:8000"
    environment:
      USING_DB: postgres
      PG_CONFIG: "postgres://resman:<db password>@db:5432/"
      WHOOSH_PATH: /data/whoosh_index
      S3_CONFIG: https://<access_key>:<secret_key>@<s3_host>:<s3_port>/
      S3_BUCKET: resman
      IMAGE_CACHE_SIZE: 3 # Set value by your memory
    command: ["python", "manage.py", "runserver", "--noreload", "0.0.0.0:8000"]
    volumes:
      - "<Your API Data Path>:/data"
```

### P.S.

- We didn't start S3 server here, but I have some recommendations of S3-compatible servers
  - [Minio](https://min.io/): Good for development
    - Performance restricted by the FS you're using
  - [SeaweedFS](https://github.com/chrislusf/seaweedfs): Easy to use while managing 0.1~10 Terabytes data even in single node mode
    - Easy to migrate and expand
    - Hard to delete files clearly and compact the storage
- Migrating from SQLite to MySQL/PostgreSQL
  - (Using SQLite) `manage.py dumpdata > data.json`
  - (Using MySQL/PostgreSQL) `manage.py migrate`
  - (Using MySQL/PostgreSQL) `manage.py loaddata data.json`
  
## Configurations

### Environment Variables

|Environment Variable|Comment|Example|
|---|---|---|
|DEV_MODE|0:deploy mode，non-zero: debugging mode|1|
|USING_DB|Database type, sqlite3/mysql/postgres|sqlite3|
|MYSQL_CONFIG|MySQL Connection config|mysql://resman:resman_password@127.0.0.1:3306/|
|SQLITE3_CONFIG|SQLite3 Database file path|/app/db.sqlite3|
|PG_CONFIG|MySQL Connection config|postgres://resman:resman_password@127.0.0.1:5432/|
|S3_CONFIG|S3 Object storage configuration|http://<access_key>:<secret_key>@127.0.0.1:9000/|
|S3_BUCKET|S3 Bucket|resman|
|WHOOSH_PATH|Whoosh Index file fath|/app/whoosh_index/|

## Event Definition and Logging

### Impression

- event_type: impression
- media_type: novel/video/image
- data:

```json5
{
  "query": "xxx",
  "page_size": "n",
  "page_id": "p",
  "similar_words": "sw",
  "like_only": true,
  "search_field": "full_text/...",
  "connector": "or/andmaybe/and/contains_or",
  "result": ["list of integer ids"]
}
```

### Page View

- event_type: page_view
- media_type: novel/video/image
- data:

```json5
{
  "id": 1 // PK of object
}
```

### Reaction

- event_type: reaction
- media_type: novel/video/image
- data:

```json5
{
  "id": 1, // PK of object
  "original_status": "original status",
  "command": "set like or dislike",
}
```

### Fetch Media

#### Image

- event_type: fetch_media
- media_type: image
- data:

```json5
{
  "id": 1 // PK of image
}
```

#### Video

- event_type: fetch_media
- media_type: video
- data:

```json5
{
  "id": 1, // PK of video
  "content_range": 123,
  "content_length": 456
}
```

#### Novel

- event_type: fetch_media
- media_type: novel
- data:

```json5
{
  "id": 1, // PK of video
  "page_size": 4000,
  "page_id": 1,
  "page_count": 12,
  "character_count": 4000
}
```


## Reference

### 中文自然语言处理

- [结巴中文分词](https://github.com/fxsjy/jieba)
- [中文停用词](https://github.com/goto456/stopwords)
- [敏感词列表](https://github.com/57ing/Sensitive-word)
- Word2Vec模型采用爬虫爬取的数据清洗分词后训练，数据较大不开放
    - 实验表明，仅仅使用标题+评论内容进行训练的效果比直接使用小说训练好，或许是因为更加能捕捉到标题的特征
    - 训练参数： `-window 11 -threads 10 -cbow 0 --size 30 --iter 15 --min-count 10`
  
### Code Snippet
- [Python - Django: Streaming video/mp4 file using HttpResponse](https://stackoverflow.com/questions/33208849/python-django-streaming-video-mp4-file-using-httpresponse)
