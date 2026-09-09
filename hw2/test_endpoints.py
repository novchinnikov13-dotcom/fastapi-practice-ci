import pytest
from hw1.models import Client, Parking, CParking
from hw1.init import db

@pytest.mark.parametrize("path", ["/clients", "/clients/1"])
def test_all_get_endpoints_return_200(client, app, path):  # <--- ВОТ ЗДЕСЬ ДОБАВЛЕН 'path'
    # Для эндпоинта /clients/1 база должна быть не пустой, иначе вернет 404
    if path == "/clients/1":
        with app.app_context():
            c = Client(name="Test", surname="User")
            db.session.add(c)
            db.session.commit()
    
    resp = client.get(path)
    assert resp.status_code == 200


def test_create_client(client, app):
    with app.app_context():
        clients_prev = Client.query.count()

    resp = client.post(
        "/clients",
        json={
            "name": "New",
            "surname": "Client",
            "credit_card": "1111 2222",
            "car_number": "ZZZ999",
        },
    )
    assert resp.status_code == 201

    with app.app_context():
        with_new_client = Client.query.count()
        assert with_new_client == clients_prev + 1


def test_create_parking(client, app):
    with app.app_context():
        parking_prev = Parking.query.count()

    resp = client.post(
        "/parkings",
        json={
            "address": "Kitay Gorod",
            "opened": True,
            "count_places": 11,
            "count_available_places": 10,
        },
    )

    assert resp.status_code == 201

    with app.app_context():
        with_new_park = Parking.query.count()
        assert with_new_park == parking_prev + 1


def test_in_parking(client, app):
    """Тест заезда: сначала создаем клиента и парковку, потом делаем запрос"""
    with app.app_context():
        # 1. Создаем данные вручную в БД
        c = Client(name="Ivan", surname="Petrov")
        p = Parking(address="Test Street", opened=True, count_places=5, count_available_places=5)
        
        db.session.add(c)
        db.session.add(p)
        db.session.commit()
        
        client_id = c.id
        parking_id = p.id
        free_parking_start = p.count_available_places
        in_parking_start = CParking.query.count()

    # 2. Делаем запрос на заезд
    resp = client.post("/client_parkings", json={"client_id": client_id, "parking_id": parking_id})
    assert resp.status_code == 201

    # 3. Проверяем изменения
    with app.app_context():
        parking_obj = Parking.query.get(parking_id)
        new_in_parking = CParking.query.count()
        
        assert parking_obj.count_available_places == free_parking_start - 1
        assert new_in_parking == in_parking_start + 1


def test_out_parking(client, app):
    """Тест выезда: создаем данные, делаем заезд, потом выезд"""
    with app.app_context():
        # 1. Создаем данные
        c = Client(name="Anna", surname="Smirnova")
        p = Parking(address="Another Street", opened=True, count_places=5, count_available_places=5)
        
        db.session.add(c)
        db.session.add(p)
        db.session.commit()
        
        client_id = c.id
        parking_id = p.id

        # 2. Имитируем заезд (так как у нас нет готового эндпоинта для теста заезда внутри этого теста, 
        # мы можем либо вызвать тот же POST, либо добавить запись напрямую. 
        # Проще вызвать тот же POST запрос, который мы уже тестировали)
        resp_in = client.post("/client_parkings", json={"client_id": client_id, "parking_id": parking_id})
        assert resp_in.status_code == 201
        
        free_parking_start = p.count_available_places # Это значение уже обновилось после POST? Нет, в памяти объекта p оно старое.
        # Перечитаем из БД актуальное состояние
        parking_after_in = Parking.query.get(parking_id)
        free_parking_before_out = parking_after_in.count_available_places
        
    # 3. Делаем запрос на выезд
    resp_out = client.delete("/client_parkings", json={"client_id": client_id, "parking_id": parking_id})
    assert resp_out.status_code == 200

    # 4. Проверяем изменения
    with app.app_context():
        parking_obj = Parking.query.get(parking_id)
        record = CParking.query.filter_by(client_id=client_id, parking_id=parking_id).first()
        
        assert parking_obj.count_available_places == free_parking_before_out + 1
        assert record.time_out is not None
