# ResMan

一个开源的资源管理网站

## 支持功能

- 图帖搜索、展示
- 视频搜索、流媒体展示
- 小说的搜索和阅读

## 运行方法

环境变量配置

|变量名称|说明|例子|
|---|---|---|
|DEV_MODE|0-部署模式，非0-调试模式|1|
|USING_DB|数据库类型，sqlite3/mysql/postgres|sqlite3|
|MYSQL_CONFIG|MySQL 数据连接配置|mysql://resman:resman_password@127.0.0.1:3306/|
|SQLITE3_CONFIG|SQLite3 数据库文件路径|/app/db.sqlite3|
|PG_CONFIG|MySQL 数据连接配置|postgres://resman:resman_password@127.0.0.1:5432/|
|S3_CONFIG|S3 文件系统配置|http://resman:resman_password@127.0.0.1:9000/|
|S3_BUCKET|S3 Bucket|resman|
|WHOOSH_PATH|Whoosh 索引路径|/app/whoosh_index/|


## 参考资料

### 中文自然语言处理

- [结巴中文分词](https://github.com/fxsjy/jieba)
- [中文停用词](https://github.com/goto456/stopwords)
- [敏感词列表](https://github.com/57ing/Sensitive-word)
- Word2Vec模型采用爬虫爬取的数据清洗分词后训练，数据较大不开放
    - 实验表明，仅仅使用标题+评论内容进行训练的效果比直接使用小说训练好，或许是因为更加能捕捉到标题的特征
    - 训练参数： `-window 11 -threads 10 -cbow 0 --size 30 --iter 15 --min-count 10`
    

### 代码片段

- [Python - Django: Streaming video/mp4 file using HttpResponse](https://stackoverflow.com/questions/33208849/python-django-streaming-video-mp4-file-using-httpresponse)
