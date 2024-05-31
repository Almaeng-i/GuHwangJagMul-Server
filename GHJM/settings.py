"""
Django settings for GHJM project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os, json
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path
from datetime import timedelta      # JWT 사용됨


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# secret key path
secret_file = os.path.join(BASE_DIR, 'secrets.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())
    
def get_secret(setting, secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} enviornment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret("SECRET_KEY",secrets)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

KAKAO_REST_API_KEY = get_secret('KAKAO_REST_API_KEY', secrets)
STATE = "random_string"        # user의 로그인 여부를 판단하기 위한 코드

# Kakao Callback URI
KAKAO_CALLBACK_URI = get_secret('KAKAO_CALLBACK_URI', secrets)

# Kakao Client Secret
KAKAO_SECRET_KEY = get_secret('KAKAO_SECRET_KEY', secrets)

# BASE_URL
SERVER_BASE_URL = get_secret('SERVER_BASE_URL', secrets)

# Access Token Expire time
ACCESS_EXPIRE_TIME = get_secret('ACCESS_EXPIRE_TIME', secrets)

# Refresh Token Expire time
REFRESH_EXPIRE_TIME = get_secret('REFRESH_EXPIRE_TIME', secrets)

ALGORITHM = get_secret('ALGORITHM', secrets)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    
    # My App
    "accounts",
    "almaengI",
    "userprofile",
    'thirdparty',
    
    # DRF 
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    
    # DR-Auth
    'dj_rest_auth',
    'dj_rest_auth.registration',
    
    # DR-Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.kakao',        # kakao provider 추가
    
    # oauth2
    'oauth2_provider',
    
    # AWS 
    'storages',
]

# AWS Setting
AWS_REGION = get_secret('AWS_REGION', secrets)
AWS_STORAGE_BUCKET_NAME = get_secret('AWS_STORAGE_BUCKET_NAME', secrets)
AWS_ACCESS_KEY = get_secret('AWS_ACCESS_KEY', secrets) 
AWS_SECRET_ACCESS_KEY = get_secret('AWS_SECRET_ACCESS_KEY', secrets) 
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME, AWS_REGION)
AWS_BUCKET_ROOT_FOLDER_NAME = get_secret('AWS_BUCKET_ROOT_FOLDER_NAME', secrets)
DEFAULT_FILE_STORAGE = get_secret('DEFAULT_FILE_STORAGE', secrets)
MEDIA_URL = 'https://%s/media/' % AWS_S3_CUSTOM_DOMAIN
DEFAULT_PROFILE_URL = get_secret('DEFAULT_PROFILE_URL', secrets)
RECEIVE_IMG_ENDPOINT = get_secret('RECEIVE_IMG_ENDPOINT', secrets)
BASE_S3_URL = get_secret('BASE_S3_URL', secrets)


AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = False     
AWS_QUERYSTRING_AUTH = False       # 정적인 url 생성하여 시간이 지나도 img에 접근 가능하게끔.


SITE_ID = 1
AUTH_USER_MODEL = 'accounts.CustomUser'


SOCIALACCOUNT_PROVIDERS = {
    'kakao': {
        'APP': {
            'client_id': get_secret('KAKAO_CALLBACK_URI',secrets),
            'secret': get_secret('KAKAO_SECRET_KEY',secrets),
            'key': ''
        }
    }
}

ACCOUNT_USER_MODEL_USERNAME_FIELD = None        # username 필드 사용 x
ACCOUNT_EMAIL_REQUIRED = True                   # email 필드 사용 o
ACCOUNT_USERNAME_REQUIRED = False               # username 필드 사용 x
ACCOUNT_AUTHENTICATION_METHOD = 'email'


# JWT Setting
REST_USE_JWT = True


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'allauth.account.middleware.AccountMiddleware',         # allauth middleware 추가
    'oauth2_provider.middleware.OAuth2TokenMiddleware',     # oauth middleware 추가
    'accounts.middleware.AccessTokenMiddleware',
    
]

ROOT_URLCONF = "GHJM.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "GHJM.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": get_secret("MYSQL_NAME", secrets),
        "USER" : get_secret("MYSQL_USER", secrets),
        "PASSWORD" : get_secret("MYSQL_PW", secrets),
        "HOST" : get_secret("MYSQL_HOST", secrets),
        "PORT" : get_secret("MYSQL_PORT", secrets)
    }
}


# Redis settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',     # cache.set() 사용시 자동 저장시켜줌.
        'LOCATION': 'redis://127.0.0.1:6379',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
        
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
