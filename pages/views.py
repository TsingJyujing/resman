from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from utils.http import debug_api, response_json


@debug_api
@login_required
def test_page(request: HttpRequest):
    return render(request, "test.html")


@debug_api
@response_json
def test_api(request: HttpRequest):
    return {
        "image_list": [
            {
                "img_url": "https://raw.githubusercontent.com/TsingJyujing/blogs/master/img/2020-05-05-18-59-17.png",
                "name": "qbittorrent",
            },
            {
                "img_url": "https://github.com/TsingJyujing/blogs/blob/master/img/2020-05-05-19-15-01.png",
                "name": "bandit formula"
            }
        ],
        "book_list": [
            dict(
                pk=i,
                book_name=f"Book-{i}",
                add_time=f"Add-{i}"
            )
            for i in range(10)
        ],
        "error_num": 0
    }
