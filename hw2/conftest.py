import pytest
from flask import Flask
from hw1.init import db
# Импортируем функцию, которая вешает роуты
from hw2.app import init_routes  

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 1. Инициализируем базу данных
    db.init_app(app)

    # 2. !!! ГЛАВНОЕ ИЗМЕНЕНИЕ: Вешаем все роуты на это приложение !!!
    init_routes(app)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
