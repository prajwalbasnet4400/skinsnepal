from pathlib import Path
import os
import dotenv
import django_heroku

dotenv.load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

INVENTORY_ITEM = 'https://steamcommunity.com/id/theonionknight4400/inventory/#730_2_{assetid}'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get('SECRET_KEY')

FLOAT_API = "https://api.csgofloat.com/?url={inspect_url}"
DEBUG = bool(os.environ.get('DEBUG',0))
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split()
AUTH_USER_MODEL = 'user.User'

# Application definition
ASGI_APPLICATION = 'steam_marketplace.asgi.application'
INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'chat',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',


    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'debug_toolbar',
    'django_filters',
    'django_q',

    'crispy_forms',
    # 'social_django',

    'user',
    'csgo',
    'message',
    'api'
]
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}
INTERNAL_IPS = [
    '127.0.0.1',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'steam_marketplace.urls'
CORS_ORIGIN_ALLOW_ALL = True
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
WSGI_APPLICATION = 'steam_marketplace.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'steam',
        'HOST': '127.0.0.1',
        'PORT': 5432,
        'USER': 'postgres',
        'PASSWORD': 'mysecretpassword'

    }
}
Q_CLUSTER = {
    'name': 'steam',
    'workers': 3,
    'recycle': 500,
    'timeout': 60,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 3,
    'label': 'Django Q',
    'redis': {
        'host': '192.168.1.100',
        'port': 6379,
        'db': 0, }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
MEDIA_URL = '/uploads/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STEAM_AVATAR_URL = 'https://community.akamai.steamstatic.com/economy/image/'

DEFAULT_FROM_EMAIL = 'TheOnionKnight@academygaming.org'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

CRISPY_TEMPLATE_PACK = 'bootstrap4'
USD_RATE = 100

KHALTI_PUBLIC_KEY = os.environ.get('KHALTI_PUBLIC_KEY')
KHALTI_SECRET_KEY = os.environ.get('KHALTI_SECRET_KEY')

STEAM_API_KEY = os.environ.get('STEAM_API_KEY')

KHALTI_VERIFICATION_URL = 'https://khalti.com/api/v2/payment/verify/'
KHALTI_LIST_URL = 'https://khalti.com/api/v2/merchant-transaction/'
KHALTI_DETAIL_URL = 'https://khalti.com/api/v2/merchant-transaction/<idx>/'
KHALTI_STATUS_URL = 'https://khalti.com/api/v2/payment/status/'

LOGIN_REDIRECT_URL = ''
LOGIN_URL = '/user/auth/steam/'

CORS_ALLOW_ALL_ORIGINS = True

SITE_URL = 'http://127.0.0.1:8000'
django_heroku.settings(locals())


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}