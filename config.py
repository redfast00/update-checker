import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True

# This gets overridden by the second config, for debugging purposes only!
SECRET_KEY = 'you-will-never-guess'

# Contact information for the scraper
CONTACT_INFO = "redfast00@gmail.com"

# Update interval in seconds
UPDATE_INTERVAL = 30 * 60
# Number of updates of a feed
NUM_UPDATES = 100

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False