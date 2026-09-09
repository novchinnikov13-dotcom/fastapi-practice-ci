from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from hw2.app import init_routes  # импортируем функцию
    from hw1.models import Client, CParking, Parking

    with app.app_context():
        db.create_all()

    init_routes(app)

    return app
