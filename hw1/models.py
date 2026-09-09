from datetime import datetime
from typing import Dict, Any
from hw1.init import db
class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50), nullable=True)
    car_number = db.Column(db.String(10), nullable=True)

    parkings = db.relationship('CParking', back_populates = 'client', cascade="all, delete-orphan")


    def __repr__(self):
        return f"Клиент {self.name} {self.car_number}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}


class Parking(db.Model):
    __tablename__ = 'parking'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, default=True)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    clients = db.relationship('CParking', back_populates = 'parking', cascade="all, delete-orphan")

    def __repr__(self):
        return f"Парковка {self.id} {self.address}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}

class CParking(db.Model):
    __tablename__ = 'client_park'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("client.id", ondelete="CASCADE"),
        nullable=False,
    )
    parking_id = db.Column(
        db.Integer,
        db.ForeignKey("parking.id", ondelete="CASCADE"),
        nullable=False,
    )
    time_in = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    time_out = db.Column(db.DateTime, nullable=True)

    client =  db.relationship('Client', back_populates = 'parkings')
    parking = db.relationship('Parking', back_populates = 'clients')

    def __repr__(self) -> str:
        return (
            f"<ClientParking id={self.id} client_id={self.client_id} "
            f"parking_id={self.parking_id} time_in={self.time_in} time_out={self.time_out}>"
        )
