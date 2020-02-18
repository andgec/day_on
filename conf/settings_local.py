import os
'''
# Uncomment for testing migrations
from .settings import BASE_DIR

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'vitasbygg_dev_drift2'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', None),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', 5433),
        'CONN_MAX_AGE': 20,  # 20 seconds connection age.
    }
}

MEDIA_ROOT = '/home/andrius/workspace/python/data_bucket/co_manager/media'
MEDIA_URL = '/media/'

INTERNAL_IPS=['127.0.0.1']