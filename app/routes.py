from app import app
from app import db
from flask import render_template,request, session, redirect, url_for
from app.models import User, Admin, ParkingLot, ParkingSpot, Reservation
from functools import wraps
import json
import datetime, timedelta
import dateutil.parser
import pytz


def logged_in(f):
	@wraps(f)
	def wrapper():
		if 'logged_in' in session and session['logged_in'] == True:
			print("Operation allowed : {}".format(f))
			return f()
		else:
			print("Operation unallowed without login: {}".format(f))
			return redirect(url_for('login'))

	print("logged_in decorator called")
	return wrapper

@app.route('/')
@app.route('/index/')
@logged_in
def index():
	# no_family = check_no_family(session['username'])
	return render_template('index.html',username = session['username'])

@app.route('/register/')
def register():
	return render_template('register.html')

@app.route('/admin_login/')
def admin_login():
	return render_template('admin_login.html')

@app.route('/admin/')
def admin():
	return render_template('admin.html',username = session['username'])

@app.route('/post_admin_login/',methods=['POST'])
def post_admin_login():
	try:
		session['logged_in'] = ''
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		username = data['username']
		password = data['password']

		user = Admin.query.filter_by(username=username).first()

		if user is not None:
			if user.password == password:
				print ('logged in')
				session['logged_in'] = True
				session['username'] = username
				return json.dumps({'status' : 'success'})
			else:
				print ('password wrong')
				return json.dumps({'status' : 'failure'})
		else:
			print ('did not find admin')
			return json.dumps({
				'status' : 'failure'
				})

	except Exception as e:
		print ('post_login ERROR: {}'.format(e))
		return json.dumps({
			'status' : 'failure'
			})

@app.route('/post_register/',methods=['POST'])
def post_register():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		username = data['username']
		email = data['email']
		password = data['password']
		first_name = data['first_name']
		last_name = data['last_name']

		new_user = User(username=username, first_name = first_name, last_name = last_name, email=email,password=password)
		db.session.add(new_user)
		db.session.commit()

		print ('post_register added user:\n')
		print ('username: {}'.format(username))
		print ('email: {}'.format(email))
		print ('password: {}'.format(password))

		return json.dumps({
			'status' : 'success'
			})

	except Exception as e:
		print ('post_register ERROR: {}'.format(e))
		return json.dumps({
			'status' : 'failure'
			})

@app.route('/login/')
def login():
	return render_template('login.html')

@app.route('/post_login/',methods=['POST'])
def post_login():
	try:
		session['logged_in'] = ''
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		username = data['username']
		password = data['password']

		print ('post_login tried user:\n')
		print ('username: {}'.format(username))
		print ('password: {}'.format(password))

		user = User.query.filter_by(username=username).first()

		#check if user exists
		if user is not None:
			#check if password is valid
			if user.password == password:
				#saving session variables
				session['logged_in'] = True
				session['username'] = username
				#returning response to login.js
				return json.dumps({'status' : 'success'})
			else:
				print ('password wrong')
				return json.dumps({'status' : 'failure'})
		else:
			print ('did not find user')
			return json.dumps({
				'status' : 'failure'
				})

	except Exception as e:
		print ('post_login ERROR: {}'.format(e))
		return json.dumps({
			'status' : 'failure'
			})

def get_current_user():
	#get current user from db
	user = User.query.filter_by(username=session['username']).first()
	return user

def generate_parking_spots(count, parking_lot_id):
	#generate parking spots for db
	for index in range(0,count):
		new_parking_spot = ParkingSpot(parking_lot_id = parking_lot_id, 
										index_in_parking_lot = index,
										reserved = False)

		db.session.add(new_parking_spot)

	db.session.commit()

#uncomment to generate spots after resetting db
# generate_parking_spots(51,1)
# generate_parking_spots(38,1)

@app.route('/query_parking_spots/', methods=['POST'])
def query_parking_spots():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)
		parking_lot_name = data['parking_spot_name'];

		parking_lot = ParkingLot.query.filter_by(parking_lot_name = parking_lot_name).first()

		parking_spots = ParkingSpot.query.filter_by(parking_log_id = parking_lot.id).all()

		print('query_parking_spots result for parking lot {}:'.format(parking_lot.id))
		print(parking_spots)

		parking_spots_list = []

		#generate list to send back to client
		for parking_spot in parking_spots:
			parking_spots_list.append({"id":parking_spot.id, "start":parking_spot.start_datetime,"end":parking_spot.end_datetime})

		events_dict = json.dumps({"events" : events_list})

		print('query_events events JSON:')
		print(json.dumps(events_dict))

		return json.dumps({'status':'success','events':events_dict})

	except Exception as e:
		print('query_parking_spots ERROR: {}'.format(e))


#reservations are also called by the named of events
@app.route('/post_events/',methods=['POST'])
def post_events():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)
		
		parking_spot_id = int(data['parking_spot'])
		parking_lot_name = data['parking_lot']

		parking_lot = ParkingLot.query.filter_by(parking_lot_name=parking_lot_name).first()

		print('parking_lot: {}'.format(parking_lot))

		#query parking spot for reservation
		parking_spot = ParkingSpot.\
							query.\
							filter(ParkingSpot.parking_lot_id == parking_lot.id).\
							filter(ParkingSpot.index_in_parking_lot == parking_spot_id).\
							first()

		print('Parking lot: {}'.format(parking_lot))
		print('Parking spot: {}'.format(parking_spot))

		user = get_current_user()

		user_id = user.id

		start_date = data['start_date']
		end_date = data['end_date']

		repeat_reservation = None
		#try and see if repeat_reservation parameter was sent in request
		try:
			repeat_reservation = data['repeat_reservation']
		except Exception as e:
			pass


		if repeat_reservation != None:
			#initiate list of dates to create reservations at
			reservation_dates = [start_date]
			#clone start date into new date
			new_date = dateutil.parser.parse(start_date)

			#create list of reservation dates for repeating reservations
			for i in range(0, int(repeat_reservation)-1):
				new_date = new_date + datetime.timedelta(days=1)
				reservation_dates.append(new_date.strftime("%a, %d %b %Y %H:%M:%S GMT"))

			print('post_events Reservation dates:')
			reservations = []
			#createa objects for all resrvation
			for start_date in reservation_dates:
				end_date = (dateutil.parser.parse(start_date) + datetime.timedelta(hours=2)).strftime("%a, %d %b %Y %H:%M:%S GMT")

				new_reservation = Reservation(user_id = user_id, 
											parking_spot_id = parking_spot.id, 
											start_datetime = start_date,
											end_datetime = end_date)

				reservations.append(new_reservation)

			#errors list holds reservations that couldn't created because the spot was already reserved at that date and time
			errors = []
			for reservation in reservations:
				if check_if_spot_is_reserved(reservation.parking_spot_id,reservation.start_datetime):
					errors.append(reservation.start_datetime)
				else:
					db.session.add(reservation)
					db.session.commit()

		else:
			new_reservation = Reservation(user_id = user_id, 
										parking_spot_id = parking_spot.id, 
										start_datetime = start_date,
										end_datetime = end_date)

			db.session.add(new_reservation)
			db.session.commit()

			errors = []

		print('All reservations:')
		print(Reservation.query.all())

		return json.dumps({'status':'success', 'errors' : errors})

	except Exception as e:
		print('post_events ERROR: {}'.format(e))
		return json.dumps({'status' : 'failure' })


def check_if_spot_is_reserved(parking_spot_id, start_date):

	reservation = Reservation.query.\
							filter(Reservation.parking_spot_id == parking_spot_id).\
							filter(Reservation.start_datetime == start_date).\
								first()

	if reservation is None:
		return False
	else:
		print(reservation)
		return True


#query all reservations for current user
@app.route('/query_reservations/',methods=['POST'])
def query_reservations():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		user = get_current_user() 

		reservations = user.reservations

		reservations_list = []

		for reservation in reservations:
			parking_spot = ParkingSpot.query.filter_by(id=reservation.parking_spot_id).first()
			parking_lot = ParkingLot.query.filter_by(id=parking_spot.parking_lot_id).first()

			parking_lot_name = parking_lot.parking_lot_name
			parking_spot_index = parking_spot.index_in_parking_lot

			print('[RESERVATION]:')
			print('index in lot: {}'.format(parking_spot_index))
			print('lot name: {}'.format(parking_lot_name))

			reservations_list.append({"id":reservation.id,
										"start":reservation.start_datetime,
										"end":reservation.end_datetime,
										"parking_lot_name":parking_lot_name,
										'parking_spot_index' : parking_spot_index})

		reservations_dict = json.dumps({"reservations" : reservations_list})

		print('query_reservations reservations JSON:')
		print(json.dumps(reservations_dict))

		return json.dumps({'status':'success','reservations':reservations_dict})

	except Exception as e:
		print('query_reservations ERROR: {}'.format(e))
		return json.dumps({'status':'failure'})

@app.route('/query_reservations_for_spot/',methods=['POST'])
def query_reservations_for_spot():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		user = get_current_user() 

		parking_spot_id = int(data['parking_spot_id'])
		parking_lot_name = data['parking_lot_name']

		parking_lot = ParkingLot.query.filter_by(parking_lot_name=parking_lot_name).first()

		parking_spot = ParkingSpot.\
							query.\
							filter(ParkingSpot.parking_lot_id == parking_lot.id).\
							filter(ParkingSpot.index_in_parking_lot == parking_spot_id).\
							first()

		print('Parking lot: {}'.format(parking_lot))
		print('Parking spot: {}'.format(parking_spot))

		reservations = Reservation.query.filter_by(parking_spot_id=parking_spot.id).all()

		print('query_reservation_for_spot reservations: ')
		print(reservations)

		reservations_list = []

		for reservation in reservations:
			parking_spot = ParkingSpot.query.filter_by(id=reservation.parking_spot_id).first()
			parking_lot = ParkingLot.query.filter_by(id=parking_spot.parking_lot_id).first()

			parking_lot_name = parking_lot.parking_lot_name
			parking_spot_index = parking_spot.index_in_parking_lot

			print('[RESERVATION]:')
			print('index in lot: {}'.format(parking_spot_index))
			print('lot name: {}'.format(parking_lot_name))

			reservations_list.append({"id":reservation.id,
										"start":reservation.start_datetime,
										"end":reservation.end_datetime,
										"parking_lot_name":parking_lot_name,
										'parking_spot_index' : parking_spot_index})

		reservations_dict = json.dumps({"reservations" : reservations_list})

		print('query_reservations reservations JSON:')
		print(json.dumps(reservations_dict))

		return json.dumps({'status':'success','reservations':reservations_dict})

	except Exception as e:
		print('query_reservations_for_spot ERROR: {}'.format(e))
		return json.dumps({'status':'failure'})

@app.route('/delete_event/',methods=['POST'])
def delete_events():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		id = data['id']

		# event = List.query.filter_by(id=id).first()

		reservation = Reservation.query.filter_by(id=id).first()

		print('delete_events reservation: {}'.format(reservation))

		db.session.delete(reservation)
		db.session.commit()

		# print('got here3')

		return json.dumps({'status':'success'})

	except Exception as e:
		print('delete_events ERROR: {}'.format(e))
		return json.dumps({'status':'failure'})

@app.route('/query_personal_data/',methods=['POST'])
def query_personal_data():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		user = get_current_user()

		first_name = user.first_name
		last_name = user.last_name
		registration_plate = user.registration_plate

		data = {
			'first_name' : first_name,
			'last_name' : last_name,
			'registration_plate' : registration_plate
		}

		return json.dumps(data)
	
	except Exception as e:
		print('query_personal_data ERROR: {}'.format(e))
		return json.dumps({'status':'failure'})

@app.route('/update_personal_data/',methods=['POST'])
def update_personal_data():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		first_name = data['first_name']
		last_name = data['last_name']
		registration_plate = data['registration_plate']

		user = get_current_user()
		user.first_name = first_name
		user.last_name = last_name
		user.registration_plate = registration_plate

		db.session.commit()

		return json.dumps({'status':'success'})

	except Exception as e:
		print('update_personal_data ERROR: {}'.format(e))
		return json.dumps({'status':'failure'})


@app.route('/query_parking_lot_stats/',methods=['POST'])
def query_parking_lot_stats():
	try:

		parking_lots = ParkingLot.query.all()
		currently_happening_reservations = {}
		last_month_profits = {}
		parking_lot_statuses = {}
		
		for parking_lot in parking_lots:
			#load parking spots for lot
			parking_spots = parking_lot.parking_spots
			parking_lot_closed_status = parking_lot.closed

			parking_lot_statuses[parking_lot.parking_lot_name] = parking_lot_closed_status

			print('STATUS: {}'.format(parking_lot_closed_status))

			last_month_reservations_count = 0
			currently_happening_reservations[parking_lot.parking_lot_name] = []

			for parking_spot in parking_spots:
				reservations = Reservation.query.filter_by(parking_spot_id = parking_spot.id).all()

				for reservation in reservations:
					#get reservations currently happening
					start_date = dateutil.parser.parse(reservation.start_datetime).replace(tzinfo=None)
					end_date = dateutil.parser.parse(reservation.end_datetime).replace(tzinfo=None)

					current_date = datetime.datetime.now().replace(tzinfo=None)

					if current_date > start_date and current_date < end_date:
						#we found a reservation happening right now
						print('============================= \nFound reservation happening now! {}\n==============='.format(reservation))
						currently_happening_reservations[parking_lot.parking_lot_name].append(reservation)

					#get last month's profit
					last_month_date = datetime.datetime.now().replace(tzinfo=None) - datetime.timedelta(days=30)
					# print(last_month_date)
					if start_date > last_month_date and start_date < current_date:
						# print('Found last month reservation: {}'.format(reservation))
						last_month_reservations_count += 1

					last_month_profits[parking_lot.parking_lot_name] = last_month_reservations_count*120

		print('\n===============\nCurrently happening reservations:')
		print(currently_happening_reservations)

		data_dict = {}
		
		for key,val in currently_happening_reservations.items():

			reservations_list = []

			#iterate each parking lot's reservations
			for reservation in currently_happening_reservations[key]:

				reservation_dict = {
					'user_id' : reservation.user_id,
					'parking_spot_id' : reservation.parking_spot_id
				}

				reservations_list.append(reservation_dict)

			data_dict[key] = reservations_list
		
		return json.dumps({'status':'success',
							'reservations' : data_dict,
							'last_month_profits' : last_month_profits,
							'parking_lot_statuses' : parking_lot_statuses})

	except Exception as e:
		print('query_parking_lot_stats ERROR: {}'.format(e))
		return json.dumps({'status':'failure'})



@app.route('/close_parking_lot/',methods=['POST'])
def close_parking_lot():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		parking_lot_name = data['parking_lot_name']
		parking_lot = ParkingLot.query.filter_by(parking_lot_name = parking_lot_name).first()

		print("close_parking_lot closing parking lot: {}".format(parking_lot))

		parking_lot.closed = True
		db.session.commit()

		return json.dumps({'status':'success'})

	except Exception as e:
		print('close_parking_lot ERROR: {}'.format(e))
		return json.dumps({'status':'failure'})

@app.route('/open_parking_lot/',methods=['POST'])
def open_parking_lot():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		parking_lot_name = data['parking_lot_name']
		parking_lot = ParkingLot.query.filter_by(parking_lot_name = parking_lot_name).first()

		print("close_parking_lot closing parking lot: {}".format(parking_lot))

		parking_lot.closed = False
		db.session.commit()

		return json.dumps({'status':'success'})

	except Exception as e:
		print('open_parking_lot ERROR: {}'.format(e))
		return json.dumps({'status':'failure'})

@app.route('/check_parking_lot_open/',methods=['POST'])
def check_parking_lot_open():
	try:
		JSONstring = json.dumps(request.get_json(force=True))
		data = json.loads(JSONstring)

		parking_lot_name = data['parking_lot_name']
		parking_lot = ParkingLot.query.filter_by(parking_lot_name = parking_lot_name).first()

		parking_lot_status = parking_lot.closed

		return json.dumps({'status':'success','closed' : parking_lot_status})

	except Exception as e:
		print('check_parking_lot_open ERROR: {}'.format(e))
		return json.dumps({'status':'failure'})









