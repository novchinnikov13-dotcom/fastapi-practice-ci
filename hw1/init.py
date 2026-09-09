from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from module_29_testing.hw.hw_1.models import Client, Parking, CParking
    from module_29_testing.hw.hw2.app import init_routes  # импортируем функцию

    with app.app_context():
        db.create_all()

    init_routes(app)

    return app
