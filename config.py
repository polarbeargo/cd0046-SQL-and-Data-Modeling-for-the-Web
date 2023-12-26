import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = False

# Set SQLALCHEMY_ECHO to True to see the SQL queries.
SQLALCHEMY_ECHO = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://hsin-wenchang:12345678@localhost:5432/fyyur'
