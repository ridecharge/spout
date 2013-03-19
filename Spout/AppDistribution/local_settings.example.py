SPOUT_DATA_ROOT = "/home/ubuntu/spout_data"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '%s/db/spout.db' % SPOUT_DATA_ROOT,                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

MEDIA_ROOT = "%s/media" % SPOUT_DATA_ROOT

APP_ROOT = MEDIA_ROOT + "/app"
APP_PACKAGE_ROOT = APP_ROOT + "/package"
APP_ICON_ROOT = APP_ROOT + "/icon"
APP_ASSET_ROOT = APP_ROOT + "/asset"

DSYM_ROOT = MEDIA_ROOT + "/dsym"
STATIC_ROOT =  "%s/static" % PROJECT_PATH # PROJECT_PATH is defined in settings.py and is the path that settings.py resides in
DEBUG = True
