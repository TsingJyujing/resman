from django.urls import re_path

from .views import frontend_page

app_name = "pages"

urlpatterns = [
    re_path(r'.*?', frontend_page, name='frontend_page'),
]
