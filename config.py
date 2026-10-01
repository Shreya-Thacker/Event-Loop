import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'eventloop-dev-secret-key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///eventloop.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
