import json
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse

from resman.settings import FRONTEND_BUILD_RESULT_DIR, DEV_MODE


def get_index_html_content() -> bytes:
    with open(os.path.join(FRONTEND_BUILD_RESULT_DIR, "index.html"), "rb") as fp:
        return fp.read()


INDEX_HTML_CONTENT = get_index_html_content()


@login_required
def frontend_page(request: HttpRequest):
    return HttpResponse(
        content=get_index_html_content() if DEV_MODE else INDEX_HTML_CONTENT
    )


@login_required
def current_user(request: HttpRequest):
    return HttpResponse(
        content=json.dumps({
            "id": request.user.id,
            "name": request.user.username,
        }).encode()
    )
