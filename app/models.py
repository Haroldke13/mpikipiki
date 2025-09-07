# app/models.py
from bson import ObjectId
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import mongo



# -------------------- USER MODEL --------------------
class User(UserMixin):
    def __init__(self, name, email, phone, password=None, password_hash=None, role="customer", _id=None):
        self.id = str(_id) if _id else None
        self.name = name
        self.email = email
        self.phone = phone
        # If we are creating a new user → hash password
        # If loading from DB → keep the saved hash
        if password_hash:
            self.password_hash = password_hash
        elif password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = None
        self.role = role  # "customer", "rider", "driver"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save_to_db(self):
        user_data = {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "password_hash": self.password_hash,
            "role": self.role,
        }
        if self.id:
            mongo.db.users.update_one({"_id": ObjectId(self.id)}, {"$set": user_data})
        else:
            result = mongo.db.users.insert_one(user_data)
            self.id = str(result.inserted_id)

    @staticmethod
    def get_by_email(email):
        data = mongo.db.users.find_one({"email": email})
        if data:
            return User(
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                password_hash=data["password_hash"],  # <- keep original hash
                role=data.get("role", "customer"),
                _id=data["_id"],
            )
        return None


# -------------------- RIDE REQUEST MODEL --------------------
class RideRequest:
    def __init__(self, pickup, destination, rider_id, status="pending", driver_id=None, _id=None):
        self.id = str(_id) if _id else None
        self.pickup = pickup
        self.destination = destination
        self.rider_id = rider_id
        self.status = status  # pending, accepted, in_progress, completed
        self.driver_id = driver_id

    def save_to_db(self):
        ride_data = {
            "pickup": self.pickup,
            "destination": self.destination,
            "rider_id": self.rider_id,
            "status": self.status,
            "driver_id": self.driver_id,
        }
        if self.id:
            mongo.db.rides.update_one({"_id": self.id}, {"$set": ride_data})
        else:
            result = mongo.db.rides.insert_one(ride_data)
            self.id = str(result.inserted_id)

    @staticmethod
    def get_pending_rides():
        return list(mongo.db.rides.find({"status": "pending"}))


# -------------------- DRIVER MODEL --------------------
class Driver:
    def __init__(self, user_id, availability=True, current_location=None, vehicle_details=None, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = user_id
        self.availability = availability
        self.current_location = current_location  # could be dict {lat, lng}
        self.vehicle_details = vehicle_details or {}

    def save_to_db(self):
        driver_data = {
            "user_id": self.user_id,
            "availability": self.availability,
            "current_location": self.current_location,
            "vehicle_details": self.vehicle_details,
        }
        if self.id:
            mongo.db.drivers.update_one({"_id": self.id}, {"$set": driver_data})
        else:
            result = mongo.db.drivers.insert_one(driver_data)
            self.id = str(result.inserted_id)
            
    @staticmethod
    def get_pending_rides():
        rides = list(mongo.db.rides.find({"status": "pending"}))
        for ride in rides:
            ride["_id"] = str(ride["_id"])
        return rides


    @staticmethod
    def get_available_drivers():
        return list(mongo.db.drivers.find({"availability": True}))


# -------------------- TRIP MODEL --------------------
class Trip:
    def __init__(self, ride_request_id, start_time=None, end_time=None, fare=0.0,
                 payment_status="unpaid", _id=None):
        self.id = str(_id) if _id else None
        self.ride_request_id = ride_request_id
        self.start_time = start_time or datetime.utcnow()
        self.end_time = end_time
        self.fare = fare
        self.payment_status = payment_status  # unpaid, paid

    def save_to_db(self):
        trip_data = {
            "ride_request_id": self.ride_request_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "fare": self.fare,
            "payment_status": self.payment_status,
        }
        if self.id:
            mongo.db.trips.update_one({"_id": self.id}, {"$set": trip_data})
        else:
            result = mongo.db.trips.insert_one(trip_data)
            self.id = str(result.inserted_id)

    @staticmethod
    def get_by_ride_request(ride_request_id):
        return mongo.db.trips.find_one({"ride_request_id": ride_request_id})


