from django.urls import re_path, path

from .views import frontend_page, current_user

app_name = "pages"

urlpatterns = [
    path('accounts/current', current_user, name="get_current_user"),
    re_path(r'.*?', frontend_page, name='frontend_page'),
]
