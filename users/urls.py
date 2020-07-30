from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    url(r'^login/', views.login_view, name='login'),
]