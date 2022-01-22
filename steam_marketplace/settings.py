from pathlib import Path
import os
import dotenv

dotenv.load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

INVENTORY_ITEM = 'https://steamcommunity.com/id/theonionknight4400/inventory/#730_2_{assetid}'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
FLOAT_API = "https://api.csgofloat.com/?url={inspect_url}"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['182.93.82.39','127.0.0.1','localhost']
AUTH_USER_MODEL = 'user.User'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'debug_toolbar',
    'social_django',
    'django_select2',
    'rest_framework',
    'djoser',
    'rest_framework.authtoken',
    'crispy_forms',
    'django_filters',
    'django_q',

    'user',
    'csgo',
    'message'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]


WSGI_APPLICATION = 'steam_marketplace.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/uploads/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STEAM_AVATAR_URL = 'https://community.akamai.steamstatic.com/economy/image/'


# Social Auth
SOCIAL_AUTH_STEAM_API_KEY = '2DFF519EA79AFA3CF63E51B4404B31D4'
SOCIAL_AUTH_STEAM_EXTRA_DATA = ['player']
SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social_core.backends.steam.SteamOpenId',
)
AUTHENTICATION_BACKENDS = (
    'social_core.backends.steam.SteamOpenId',
    'django.contrib.auth.backends.ModelBackend',
)
SOCIAL_AUTH_STEAM_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. In some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    # 'social_core.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',
    'user.auth_pipeline.save_profile',

    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',
)



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
LOGIN_URL = '/auth/social/login/steam/'