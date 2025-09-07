
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId
from . import mongo
from .forms import SignupForm, LoginForm, RideRequestForm, DriverAvailabilityForm
from .models import User, RideRequest, Driver, Trip

main = Blueprint("main", __name__)


# -------------------- HOME --------------------
@main.route("/")
def home():
    return render_template("home.html")


# -------------------- SIGNUP --------------------
@main.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user:
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for("main.login"))

        # Create new user
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            password=form.password.data,
            role=form.role.data
        )
        user.save_to_db()
        flash("Signup successful. Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("signup.html", form=form)


# -------------------- LOGIN --------------------
@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main.home"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)


# -------------------- LOGOUT --------------------
@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


# -------------------- RIDE REQUEST --------------------
@main.route("/request_ride", methods=["GET", "POST"])
@login_required
def request_ride():
    if current_user.role not in ["rider", "customer", "driver"]:
        flash("Only riders, customers, or drivers can request rides.", "danger")
        return redirect(url_for("main.home"))

    form = RideRequestForm()
    if form.validate_on_submit():
        ride = RideRequest(
            pickup=form.pickup.data,
            destination=form.destination.data,
            rider_id=current_user.id
        )
        ride.save_to_db()
        flash("Ride request submitted!", "success")

        # Redirect based on role
        if current_user.role in ["rider", "customer"]:
            return redirect(url_for("main.customer_dashboard"))
        elif current_user.role == "driver":
            return redirect(url_for("main.driver_dashboard"))

    return render_template("request_ride.html", form=form)



# -------------------- DRIVER DASHBOARD --------------------
from bson import ObjectId
from .forms import DriverAvailabilityForm, AcceptRideForm

@main.route("/driver", methods=["GET", "POST"])
@login_required
def driver_dashboard():
    if current_user.role != "driver":
        flash("Only drivers can access the driver dashboard.", "danger")
        return redirect(url_for("main.home"))

    availability_form = DriverAvailabilityForm()
    if availability_form.validate_on_submit():
        driver = Driver(
            user_id=current_user.id,
            availability=availability_form.availability.data,
            current_location=availability_form.current_location.data,
            vehicle_details={"info": availability_form.vehicle_details.data},
        )
        driver.save_to_db()
        flash("Driver availability updated.", "success")


    # get pending rides
    pending_rides = Driver.get_pending_rides()

    # create one accept form per ride
    accept_forms = {ride["_id"]: AcceptRideForm() for ride in pending_rides}

    return render_template(
        "driver_dashboard.html",
        form=availability_form,
        rides=pending_rides,
        accept_forms=accept_forms
    )


# -------------------- TRIP DETAILS --------------------
@main.route("/trip/<trip_id>")
@login_required
def trip_details(trip_id):
    trip = mongo.db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("main.home"))
    return render_template("trip.html", trip=trip)

@main.route("/api/ride_status/<ride_id>")
@login_required
def ride_status(ride_id):
    ride = mongo.db.rides.find_one({"_id": ObjectId(ride_id)})
    if ride:
        return {"status": ride.get("status", "unknown")}
    return {"status": "not found"}

# -------------------- CUSTOMER DASHBOARD --------------------
@main.route("/customer")
@login_required
def customer_dashboard():
    if current_user.role not in ["customer", "rider"]:
        flash("Only customers/riders can access this dashboard.", "danger")
        return redirect(url_for("main.home"))

    # Fetch this user's ride requests
    my_rides = list(mongo.db.rides.find({"rider_id": current_user.id}))

    # Check if there are available drivers
    available_drivers = Driver.get_available_drivers()

    if available_drivers:
        flash(f"{len(available_drivers)} drivers are available. They will be notified.", "success")
    else:
        flash("No drivers available at the moment. Please wait.", "warning")

    return render_template("customer_dashboard.html", rides=my_rides, drivers=available_drivers)

import random
from datetime import datetime
from bson import ObjectId

# -------------------- DRIVER ACCEPT RIDE --------------------
@main.route("/accept_ride/<ride_id>", methods=["POST"])
@login_required
def accept_ride(ride_id):
    if current_user.role != "driver":
        flash("Only drivers can accept rides.", "danger")
        return redirect(url_for("main.home"))

    ride = mongo.db.rides.find_one({"_id": ObjectId(ride_id)})
    if not ride:
        flash("Ride not found.", "danger")
        return redirect(url_for("main.driver_dashboard"))

    # Get driver's current location
    driver_doc = mongo.db.drivers.find_one({"user_id": current_user.id})
    driver_loc = driver_doc.get("current_location") if driver_doc else None

    # Generate 5-digit confirmation code
    match_code = random.randint(10000, 99999)

    # Calculate ETA (if driver location is available)
    eta = None
    if driver_loc and ride.get("pickup"):
        eta = calculate_eta(ride["pickup"], driver_loc, 40)

    # Update ride
    mongo.db.rides.update_one(
        {"_id": ObjectId(ride_id)},
        {"$set": {
            "status": "accepted",
            "driver_id": current_user.id,
            "match_code": match_code,
            "eta": eta,
            "accepted_at": datetime.utcnow()
        }}
    )

    flash("Ride accepted! Customer has been notified.", "success")
    return redirect(url_for("main.driver_dashboard"))


from math import radians, sin, cos, sqrt, atan2

def calculate_eta(pickup, driver_loc, speed_kmh=40):
    """pickup and driver_loc are strings like 'lat,lng' or 'lat,lng|place'."""
    try:
        # Handle "lat,lng|place"
        pickup_coords = pickup.split("|")[0].strip()
        driver_coords = driver_loc.split("|")[0].strip()

        lat1, lon1 = map(float, pickup_coords.split(","))
        lat2, lon2 = map(float, driver_coords.split(","))
    except Exception:
        return "30 min"  # fallback if invalid

    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    eta_minutes = int((distance / speed_kmh) * 60)
    return f"{eta_minutes} min"
