import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'eventloop-dev-secret-key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///eventloop.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'documents')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp'}
