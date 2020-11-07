from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path(r'test/login', views.test_page, name='test'),
    path(r'test/json', views.test_api, name='test'),
]