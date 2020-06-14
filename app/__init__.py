from flask import Flask
from models.models import db

app = Flask(__name__, template_folder="../templates", static_folder="../static")

if app.config["DEBUG"]:
    print(app.config["DEBUG"], "DEBUGging")
    app.config.from_object("config.DevelopmentConfig")
elif app.config["TESTING"]:
    app.config.from_object("config.TestingConfig")
else:
    app.config.from_object("config.ProductionConfig")

db.init_app(app)









# app views
from app import views

# admin views
from admin import views

# auth views
from auth import views

