import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 't(auwl)iz9o_ovf6lstrql_w)9kt@6(m_nw_nn5r3&nyvdv_!%')
MAINTENANCE_KEY = os.environ.get('MAINTENANCE_KEY', '&tk10jc)02p71+l^fv0$s$*!pljdcq#wq@^m!x82ut9!wa*$rv')

RUNTIME_ENV = os.environ.get('RUNTIME_ENV', 'local')

LOCAL_ENV = RUNTIME_ENV not in ('PROD', 'PRODUCTION', 'PROD-DEBUG', 'STAGING', 'DEV')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = str(os.environ.get('DEBUG', RUNTIME_ENV not in ('PROD', 'PRODUCTION'))).lower() in ('true', '1')

ALLOWED_HOSTS = [os.environ.get('WEB_HOST', 'localhost'), os.environ.get('WEB_HOST_2', 'localhost')]

MAINTENANCE_MODE = str(os.environ.get('MAINTENANCE', 'False')).lower() in ('true', 'yes', '1')

# Invalidating all user sessions by temporarily changing the secret key. This forces all users to log in by which they get maintenance page.
# Sessions will be restored when maintenance mode is off again (and secret key is old one again.
if MAINTENANCE_MODE:
    SECRET_KEY = MAINTENANCE_KEY


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'maintenancemode',
    'django_db_logger',
    'debug_toolbar',
    'django_select2',
    'parler',
    'wkhtmltopdf', # HowTo: https://www.jeremydaly.com/how-to-install-wkhtmltopdf-on-amazon-linux/
                   # https://downloads.wkhtmltopdf.org/0.12/0.12.5/wkhtmltox-0.12.5-1.centos6.x86_64.rpm
                   # sudo yum install wkhtmltox-0.12.5-1.centos6.x86_64.rpm
                   # Local system: if installing from regular packages then header and footer is not rendered. Check the link below:
                   # https://stackoverflow.com/questions/35617491/how-to-install-wkhtmltopdf-patched-qt-without-compiling
    'djauth',
    'inventory',
    'general',
    'receivables',
    'salary',
    'reports',
]

APP_ORDER = [
        'auth',
        'djauth',
        'general',
        'salary',
        'inventory',
        'receivables',
        'django_db_logger',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # Localization
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'co_manager.urls'

AUTH_USER_MODEL = 'djauth.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',                
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
'''
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)
'''
WSGI_APPLICATION = 'conf.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#authent-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'lt'

TIME_ZONE = 'Europe/Oslo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES=(
    ('nb', 'Norwegian Bokmål'),
    ('lt', 'Lithuanian'),
)

PARLER_LANGUAGES = {
    None: (
        {'code': 'lt',},
        {'code': 'nb',},
    ),
    'default': {
        'fallbacks': ['lt', 'nb'],    # defaults to PARLER_DEFAULT_LANGUAGE_CODE
        'hide_untranslated': False,   # the default; let .active_translations() return fallbacks too.
    }
}

LOCALE_PATHS = (
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'db_log': {
            'level': 'INFO',
            'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
        },
    },
    'loggers': {
        'db': {
            'handlers': ['db_log'],
            'level': 'INFO'
        }
    }
}


MAX_DIGITS_PRICE        = 14
MAX_DIGITS_CURRENCY     = 14
MAX_DIGITS_QTY          = 14

DECIMAL_PLACES_PRICE    = 4
DECIMAL_PLACES_CURRENCY = 2
DECIMAL_PLACES_QTY      = 3

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

LOGIN_URL = '/accounts/login/?next=/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

TIMELIST_LINES_PER_PAGE = 28

try:
    if LOCAL_ENV:
        from .settings_local import *

    if RUNTIME_ENV in ('PROD', 'PRODUCTION', 'PROD-DEBUG'):
        from .settings_production import *

    if RUNTIME_ENV == 'STAGING':
        from .settings_staging import *

    if RUNTIME_ENV == 'DEV':
        from .settings_dev import *

except ImportError:
    pass

