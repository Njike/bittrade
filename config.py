import os
import json
if not os.getenv("FLASK_DEBUG"):
    with open("/etc/config.json") as config_file:
        config = json.load(config_file)

class Config(object):
    DEBUG = False
    TESTING = False
    if not os.getenv("FLASK_DEBUG"): 
        SECRET_KEY = config["SECRET_KEY"] 
        SQLALCHEMY_DATABASE_URI = config["SQLALCHEMY_DATABASE_URI"]
        MAIL_SERVER = config["MAIL_SERVER"]
        MAIL_PORT = config["MAIL_PORT"]
        MAIL_USE_SSL = True
       # MAIL_USE_TLS = True
        MAIL_DEFAULT_SENDER = ("bittradeweb", "noreply@bittradeweb.com")
        MAIL_USERNAME = config["MAIL_USERNAME"]
        MAIL_PASSWORD = config["MAIL_PASSWORD"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/img/uploads")

    ALLOWED_IMAGE_EXTENTIONS = ["png", "jpg", "jpeg", "gif"]
    
    SESSION_COOKIE_SECURE = True

    

    
    

class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    
    SQLALCHEMY_DATABASE_URI = "sqlite:///../sqlite3.db"
    SECRET_KEY = "hello123"

    UPLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/img/uploads")

    SESSION_COOKIE_SECURE = False

    MAIL_SERVER = "localhost"
    MAIL_DEFAULT_SENDER = "noreply@localhost.com"
    MAIL_USE_SSL = False
    MAIL_PORT = 25
    # MAIL_USE_TLS = True
    MAIL_USERNAME = None
    MAIL_PASSWORD = None

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///../sqlite3.db"
    UPLOADS = f"{os.getcwd()}/static/img/uploads"

    SESSION_COOKIE_SECURE = False
