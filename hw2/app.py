from datetime import datetime

from flask import request, jsonify
from sqlalchemy import select
from hw1.init import db
from hw1.models import Client, Parking, CParking
from sqlalchemy import select


def init_routes(app):

    @app.route("/clients", methods=["GET"])
    def get_clients_handler():
        clients = db.session.query(Client).all()
        clients_list = [c.to_json() for c in clients]
        return jsonify(clients_list)

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client_by_id_handler(client_id):
        client = db.session.query(Client).get(client_id)
        if not client:
            return jsonify({"error": "client not found"}), 404
        return jsonify(client.to_json())

    @app.route("/clients", methods=["POST"])
    def create_client_handler():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON clients"}), 400

        name = data.get("name")
        surname = data.get("surname")
        credit_card = data.get("credit_card")
        car_number = data.get("car_number")

        new_client = Client(
            name=name, surname=surname, credit_card=credit_card, car_number=car_number
        )

        db.session.add(new_client)
        db.session.commit()

        return "client added", 201

    @app.route("/parkings", methods=["POST"])
    def create_parking_handler():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON parkings"}), 400

        address = data.get("address")
        opened = data.get("opened")
        count_places = int(data.get("count_places"))
        count_available_places = int(data.get("count_available_places"))

        new_park = Parking(
            address=address,
            opened=opened,
            count_places=count_places,
            count_available_places=count_available_places,
        )

        db.session.add(new_park)
        db.session.commit()

        return "parking added", 201

    @app.route("/client_parkings", methods=["POST"])
    def get_parking_handler():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON parkings"}), 400
        client_id = data.get("client_id")
        parking_id = data.get("parking_id")

        if client_id is None or parking_id is None:
            return jsonify({"error": "Отсутствует client_id or parking_id"}), 400

        try:
            client_id = int(client_id)
            parking_id = int(parking_id)
        except (ValueError, TypeError):
            return jsonify({"error": "client_id и parking_id должны быть числами"}), 400

        client_add = select(Client).where(Client.id == client_id)
        client = db.session.scalars(client_add).first()
        parking_add = select(Parking).where(Parking.id == parking_id)
        parking = db.session.scalars(parking_add).first()

        if not parking:
            return jsonify({"error": f"Парковка  {parking_id} не найдена"}), 404

        if not client:
            return jsonify({"error": f"Клиент {client_id} не найден"}), 404

        if not parking.opened:
            return (
                jsonify(
                    {"error": "Парковка закрыта", "parking_address": parking.address}
                ),
                403,
            )

        if parking.count_available_places <= 0:
            return (
                jsonify(
                    {
                        "error": "нет мест",
                        "parking_address": parking.address,
                        "count_places": parking.count_places,
                        "count_available_places": 0,
                    }
                ),
                409,
            )

        parking.count_available_places -= 1

        new_cparking = CParking(
            client_id=client.id, parking_id=parking.id, time_in=datetime.now()
        )

        db.session.add(new_cparking)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Парковка зарегистрирована",
                    "client_name": client.name,
                    "parking_address": parking.address,
                    "remaining_places": parking.count_available_places,
                }
            ),
            201,
        )

    @app.route("/client_parkings", methods=["DELETE"])
    def out_parking_handler():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON parkings"}), 400
        client_id = data.get("client_id")
        parking_id = data.get("parking_id")

        if client_id is None or parking_id is None:
            return jsonify({"error": "Отсутствует client_id or parking_id"}), 400

        try:
            client_id = int(client_id)
            parking_id = int(parking_id)
        except (ValueError, TypeError):
            return jsonify({"error": "client_id и parking_id должны быть числами"}), 400

        get_parking = (
            db.session.query(CParking)
            .filter_by(client_id=client_id, parking_id=parking_id)
            .first()
        )

        if get_parking is None:
            return jsonify({"error": "client_parking entry not found"}), 404

        if get_parking.time_out is not None:
            return jsonify({"error": "client already left parking"}), 400

        get_parking.time_out = datetime.now()

        parking_add = select(Parking).where(Parking.id == parking_id)
        parking = db.session.scalars(parking_add).first()

        if parking is None:
            return jsonify({"error": "parking not found"}), 404

        if parking.count_available_places < parking.count_places:
            parking.count_available_places += 1

        db.session.commit()
        return (
            jsonify(
                {
                    "message": "client left parking",
                    "client_parking": {
                        "id": get_parking.id,
                        "client_id": get_parking.client_id,
                        "parking_id": get_parking.parking_id,
                        "time_in": get_parking.time_in.isoformat(),
                        "time_out": get_parking.time_out.isoformat(),
                    },
                    "parking": {
                        "id": parking.id,
                        "count_places": parking.count_places,
                        "count_available_places": parking.count_available_places,
                    },
                }
            ),
            200,
        )
