AWS_STORAGE_BUCKET_NAME = 'vitasbygg-dev'

DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
STATIC_S3_PATH = 'static'
STATIC_URL = 'https://%s.s3.amazonaws.com/static/' % AWS_STORAGE_BUCKET_NAME

STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
DEFAULT_S3_PATH = 'media'
MEDIA_URL = 'https://%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
AWS_S3_REGION_NAME = 'eu-central-1'
AWS_S3_SIGNATURE_VERSION = 's3v4'
