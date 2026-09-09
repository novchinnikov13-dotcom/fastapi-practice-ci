from datetime import datetime
from module_29_testing.hw.hw1.models import CParking, Parking
import pytest

@pytest.mark.parametrize(
    "path",
    ["/clients", "/clients/1"])
def test_all_get_endpoints_return_200(client, path):
    resp = client.get(path)
    assert resp.status_code == 200

def test_create_client(client, db, app):
    from module_29_testing.hw.hw_1.models import Client
    with app.app_context():
        clients_prev = Client.query.count()

    resp = client.post("/clients", json={
            "name": "New",
            "surname": "Client",
            "credit_card": "1111 2222",
            "car_number": "ZZZ999",
        })
    assert resp.status_code == 201
    from module_29_testing.hw.hw_1.models import Client
    with app.app_context():
        with_new_client = Client.query.count()
        assert with_new_client == clients_prev + 1


def test_create_parking(client, db, app):
    from module_29_testing.hw.hw_1.models import Parking
    with app.app_context():
        parking_prev = Parking.query.count()
    resp = client.post('/parkings', json = {
     "address": "Kitay Gorod",
   "opened": True,
    "count_places": 11,
     "count_available_places": 10})

    assert resp.status_code == 201
    from module_29_testing.hw.hw_1.models import Parking
    with app.app_context():
        with_new_park = Parking.query.count()
        assert with_new_park == parking_prev + 1


def test_in_parking(client, db, app):
    from module_29_testing.hw.hw_1.models import Client, Parking, CParking
    with app.app_context():

        client_obj = Client.query.get(1)
        parking_obj = Parking.query.get(1)
        free_parking = parking_obj.count_available_places
        in_parking = CParking.query.count()
    resp = client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert resp.status_code == 201
    from module_29_testing.hw.hw_1.models import Client, Parking, CParking

    with app.app_context():
        parking_obj = Parking.query.get(1)
        new_in_parking = CParking.query.count()
        assert parking_obj.count_available_places == free_parking - 1
        assert new_in_parking == in_parking + 1

def test_out_parking(client, db, app):
    from module_29_testing.hw.hw_1.models import Client, Parking, CParking
    with app.app_context():
        client_obj = Client.query.get(1)
        parking_obj = Parking.query.get(1)
        free_parking = parking_obj.count_available_places
        in_parking = CParking.query.count()
    resp = client.delete("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert resp.status_code == 200
    from module_29_testing.hw.hw_1.models import Client, Parking, CParking

    with app.app_context():
        parking_obj = Parking.query.get(1)
        new_in_parking = CParking.query.count()

        parking_data = CParking.query.get(1)
        assert parking_obj.count_available_places == free_parking + 1
        assert parking_data.time_out is not None


