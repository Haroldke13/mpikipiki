# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo


# -------------------- SIGNUP FORM --------------------
class SignupForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=7, max=15)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    role = SelectField(
        "Role",
        choices=[("customer", "Customer"), ("rider", "Rider"), ("driver", "Driver")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Sign Up")


# -------------------- LOGIN FORM --------------------
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# -------------------- RIDE REQUEST FORM --------------------
class RideRequestForm(FlaskForm):
    pickup = StringField("Pickup Location", validators=[DataRequired(), Length(min=3, max=255)])
    destination = StringField("Destination", validators=[DataRequired(), Length(min=3, max=255)])
    submit = SubmitField("Request Ride")


# -------------------- DRIVER AVAILABILITY FORM --------------------
class DriverAvailabilityForm(FlaskForm):
    availability = BooleanField("Available?")
    current_location = StringField("Current Location", validators=[Length(max=255)])
    vehicle_details = StringField("Vehicle Details", validators=[Length(max=255)])
    submit = SubmitField("Update Availability")




class AcceptRideForm(FlaskForm):
    submit = SubmitField("Accept Ride")