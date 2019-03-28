from app import db
from datetime import datetime

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index=True, unique=True,nullable=False)
	email = db.Column(db.String(64),index=True, unique=True, nullable=False)
	first_name = db.Column(db.String(64), nullable=False)
	last_name = db.Column(db.String(64), nullable=False)
	password = db.Column(db.String(128), nullable=False)
	registration_plate = db.Column(db.String(128))
	reservations = db.relationship('Reservation', backref='user_reservations', lazy=True)
	
	def dump(self):
		print ("USER: {}:{} pass={}".format(self.username,self.email,self.password_hash))

class Admin(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index=True, unique=True,nullable=False)
	email = db.Column(db.String(64),index=True, unique=True, nullable=False)
	password = db.Column(db.String(128), nullable=False)

	def dump(self):
		print ("ADMIN: {}:{} pass={}".format(self.username,self.email,self.password_hash))

admin_parkinglot = db.Table('admin_parkinglot',
	db.Column('admin_id', db.Integer, db.ForeignKey('admin.id')),
	db.Column('parkinglot_id', db.Integer, db.ForeignKey('parking_lot.id'))
)

class ParkingLot(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	parking_lot_name = db.Column(db.String(120))
	closed = db.Column(db.Boolean())

	parking_spots = db.relationship('ParkingSpot', backref='parking_spots', lazy=True)

class ParkingSpot(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'),nullable=False)
	index_in_parking_lot = db.Column(db.String(4), nullable=False)
	reserved = db.Column(db.Boolean(), nullable=False)

class Reservation(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
	parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'),nullable=False)
	start_datetime = db.Column(db.String(120), nullable=False)
	end_datetime = db.Column(db.String(120), nullable=False)