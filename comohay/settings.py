"""
Django settings for comohay project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from fast_autocomplete import autocomplete_factory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "very_secret")

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = bool(int(os.environ.get("DEBUG", default=1)))

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1 [::1]").split(" ")

# Application definition

INSTALLED_APPS = [
    'ads.apps.AdsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'haystack',
    'compressor',
    'crispy_forms',
    'rest_framework',
    'categories',
    'categories.editor',
    'django_seed',
    'lazysignup',
    'actstream',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'sorl.thumbnail',
    'django_extensions',
    'django.contrib.postgres',
    'meta',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'lazysignup.backends.LazySignupBackend',
)

ROOT_URLCONF = 'comohay.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'comohay.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
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

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

# Media (uploads) files

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
    ('text/x-sass', 'django_libsass.SassCompiler'),
)

COMPRESS_ENABLED = True

COMPRESS_FILTERS = {
    'css': [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.CSSMinFilter',
    ],
    'js': [
        'compressor.filters.jsmin.JSMinFilter'
    ]
}

# Crispy forms template
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# rest framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
}

# haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack_custom.backends.custom_solr_backend.CustomSolrEngine',
        'URL': 'http://solr:8983/solr/ads',
        'ADMIN_URL': 'http://solr:8983/solr/admin/cores',
        'TIMEOUT': 60 * 5,
        # 'INCLUDE_SPELLING': True,
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "search": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CACHE_SEARCH_RESPONSE_SECONDS = 30
# caching for javascript autocomplete suggestions requests
CACHE_AUTOCOMPLETE_CLIENT = 10 * 60 * 60 * 24  # 10 days

# Celery

CELERY_BROKER_URL = 'redis://redis:6379/2'
CELERY_RESULT_BACKEND = 'redis://redis:6379/2'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    'get_proxies': {
        'task': 'ads.tasks.get_proxies',
        'schedule': crontab(minute=1)  # execute every hour at minute 1.
    },
    'crawl': {
        'task': 'ads.tasks.crawl',
        'schedule': crontab(minute=3)  # execute every hour at minute 3.
    },
    'updater': {
        'task': 'ads.tasks.updater',
        'schedule': crontab(hour=8, minute=3)  # execute every day at 4:03 AM cuban time
    }
}

# logging config

# Get loglevel from env
LOGLEVEL = os.getenv('DJANGO_LOGLEVEL', 'INFO').upper()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'level': LOGLEVEL,
            'handlers': ['console', ],
        },
    },
}

EXTERNAL_SOURCES = {
    'hogarencuba': 'hogarencuba.com',
    'bachecubano': 'bachecubano.com',
    'revolico': 'revolico.com',
    'porlalivre': 'porlalivre.com',
    'timbirichi': 'timbirichi.com',
    # 'clasificadoshlg': 'clasificadoshlg.com',
    'uncuc': '1cuc.com',
    'merolico': 'merolico.app',
}

# number of days that updater spider look for updates in an ad
AD_UPDATE_PERIOD = 5

TELEGRAM_BOT_TOKEN = 'bot_token'
TELEGRAM_BOT_GROUPS = {}

SITE_ID = 1

AUTH_USER_MODEL = 'ads.User'
LAZYSIGNUP_USER_MODEL = AUTH_USER_MODEL

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'
# ACCOUNT_USERNAME_REQUIRED = False

SOCIALACCOUNT_ADAPTER = 'comohay.socialaccount.adapter.SocialAccountAdapter'

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time',
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'en_US',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v2.12',
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# trigram similarity search threshold for duplicates
TITLE_SIMILARITY = 0.9
DESCRIPTION_SIMILARITY = 0.9
DESCRIPTION_LENGTH_DIFF = 0.15
TITLE_LENGTH_DIFF = 0.25

CUC_TO_CUP_CHANGE = 25

# django-meta settings
META_SITE_PROTOCOL = 'https'
META_SITE_DOMAIN = 'comohay.com'
META_SITE_TYPE = 'website'
META_SITE_NAME = 'ComoHay'
META_INCLUDE_KEYWORDS = ['cuba compra venta', 'cuba clasificados', 'cuba auncios', 'compra venta en cuba',
                         'clasificados en cuba', 'anuncios en cuba']
META_DEFAULT_KEYWORDS = META_INCLUDE_KEYWORDS
META_IMAGE_URL = STATIC_URL
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
META_USE_SCHEMAORG_PROPERTIES = True
META_TWITTER_TYPE = 'summary_large_image'
META_USE_TITLE_TAG = True

# THIS IS HERE BECAUSE CESAR SAYS DJANGO NO SIRVE
content_files = {
    'words': {
        'filepath': BASE_DIR + '/ads/autosuggest/suggestions',
        'compress': True  # means compress the graph data in memory
    }
}
autocomplete = autocomplete_factory(content_files=content_files)

try:
    from .settings_local import *
except:
    print('WARNING not settings_local.py file found')
