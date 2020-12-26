"""resman URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  object_name('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  object_name('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, object_name
    2. Add a URL to urlpatterns:  object_name('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("api/", include("data.urls")),
    path("pages/", include('pages.urls')),
]
