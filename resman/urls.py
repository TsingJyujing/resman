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
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

DRF_YASG_CACHE_TIMEOUT = 300
schema_view = get_schema_view(
    openapi.Info(
        title="Resman API",
        default_version="1.0",
        description="Resman API Doc",
    ),
    public=True,  # Set public to let everyone access the documentation but executions still require login
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("api/", include("data.urls")),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=DRF_YASG_CACHE_TIMEOUT),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=DRF_YASG_CACHE_TIMEOUT),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=DRF_YASG_CACHE_TIMEOUT), name="schema-redoc"
    ),
    path("", include('pages.urls')),
]
