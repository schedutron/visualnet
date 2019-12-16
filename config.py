import os

class Config(object):
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('FLASK_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
