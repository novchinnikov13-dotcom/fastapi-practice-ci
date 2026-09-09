from datetime import datetime

import pytest

from ..hw_1.init import create_app
from ..hw_1.init import db as _db
from ..hw_1.models import Client, CParking, Parking


@pytest.fixture
def app():
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"  # тестовая БД in-memory
    _app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with _app.app_context():

        _db.drop_all()
        _db.create_all()
        client = Client(
            id=1, name="Test", surname="Name", credit_card="Visa", car_number="ADC5432F"
        )
        parking = Parking(
            id=1,
            address="Berlin",
            opened=True,
            count_places=12,
            count_available_places=5,
        )
        client_park = CParking(
            client_id=1, parking_id=1, time_in=datetime.now(), time_out=None
        )
        _db.session.add(client)
        _db.session.add(parking)
        _db.session.add(client_park)
        _db.session.commit()

    yield _app

    with _app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):

    return _db
