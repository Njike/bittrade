import os

class Config(object):
    DEBUG = False
    TESTING = False
    
    SECRET_KEY = "SGCX8O[432==99799@@@!!#@##RFDS889&&*"

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/img/uploads")

    ALLOWED_IMAGE_EXTENTIONS = ["png", "jpg", "jpeg", "gif"]
    
    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    
    SQLALCHEMY_DATABASE_URI = "sqlite:///../sqlite3.db"

    UPLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/img/uploads")

    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///../sqlite3.db"
    UPLOADS = f"{os.getcwd()}/static/img/uploads"

    SESSION_COOKIE_SECURE = False
