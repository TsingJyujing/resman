"""
Django settings for resman project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import logging
import os
# Build paths inside the project like this: os.object_name.join(BASE_DIR, ...)
from urllib.parse import urlparse, unquote
from warnings import warn

log = logging.getLogger("DJANGO_SETTINGS")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xmg@8-2c-03^@3e9qrdtuu$-@j2)m^7xd(+g6u08u9vqb0ldmv'

DEBUG = int(os.environ.get("DEBUG", "1")) != 0
if DEBUG:
    warn("You're running in DEBUG mode.")


def environ_get(variable_name: str, default_value: str = None):
    """
    Get important variable from environment variables.
    The default value can only be used in debugging mode.
    :param variable_name: Environment variable name
    :param default_value: Default value in debug mode
    :return:
    """
    if not (variable_name in os.environ or DEBUG):
        raise KeyError(f"Environment variable {variable_name} not set in production model")
    return os.environ.get(variable_name, default_value)


ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "drf_yasg",
    "rest_framework",
    "data",
    "pages",
]

CORS_ORIGIN_ALLOW_ALL = DEBUG
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    "django.middleware.csrf.CsrfViewMiddleware",
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'resman.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'resman.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

USING_DB = environ_get("USING_DB", "sqlite3")

if USING_DB == "mysql":
    log.info("Using MySQL as database")
    mysql_config = urlparse(environ_get("MYSQL_CONFIG", "mysql://resman:resman_password@127.0.0.1:3306/"))
    db_config = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'resman',
        'USER': unquote(mysql_config.username),
        'PASSWORD': unquote(mysql_config.password),
        'HOST': mysql_config.hostname,
        'PORT': mysql_config.port if mysql_config.port is not None else 3306,
        'OPTIONS': {
            'charset': 'utf8mb4'
        }
    }
if USING_DB == "postgres":
    log.info("Using PostgreSQL as database")
    pg_config = urlparse(environ_get("PG_CONFIG", "postgres://resman:resman_password@127.0.0.1:5432/"))
    db_config = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'resman',
        'USER': unquote(pg_config.username),
        'PASSWORD': unquote(pg_config.password),
        'HOST': pg_config.hostname,
        'PORT': pg_config.port if pg_config.port is not None else 5432,
    }
elif USING_DB == "sqlite3":
    log.info("Using SQLite3 as database")
    db_config = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': environ_get("SQLITE3_CONFIG", os.path.join(BASE_DIR, "db.sqlite3")),
    }
else:
    raise Exception(f"Unknown db type: {USING_DB}")

DATABASES = {
    'default': db_config
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
FRONTEND_BUILD_RESULT_DIR = os.path.join(BASE_DIR, "frontend/build")
FRONTEND_STATICFILES_DIR = os.path.join(FRONTEND_BUILD_RESULT_DIR, "static")
STATICFILES_DIRS = [FRONTEND_STATICFILES_DIR]

# e.x. https://access_key:secret_key@s3.xxx.com/
DEFAULT_S3_CONFIG = environ_get("S3_CONFIG", "http://resman:resman_password@127.0.0.1:9000/")
DEFAULT_S3_BUCKET = environ_get("S3_BUCKET", "resman")

WHOOSH_PATH = environ_get(
    "WHOOSH_PATH",
    os.path.join(BASE_DIR, "whoosh_index")
)
if not os.path.isdir(WHOOSH_PATH):
    os.makedirs(WHOOSH_PATH)

CACHE_REDIS_CONFIG = environ_get("CACHE_REDIS_CONFIG")

RECSYS_MODEL_PATH = environ_get(
    "RECSYS_MODEL_PATH",
    os.path.join(BASE_DIR, "recsys_model")
)
if not os.path.isdir(RECSYS_MODEL_PATH):
    os.makedirs(RECSYS_MODEL_PATH)
