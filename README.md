# mpikipiki

A Flask + MongoDB prototype of a boda-boda (motorbike taxi) ride-hailing service, with separate
customer and driver dashboards.

## What it actually does

- **Accounts** — sign up / log in / log out with Flask-Login. A user picks one of three roles at
  signup: `customer`, `rider`, or `driver`. Passwords are hashed with Werkzeug.
- **Ride requests** — customers and riders submit a pickup and a destination (`/request_ride`),
  which is stored in the `rides` MongoDB collection with status `pending`.
- **Driver dashboard** (`/driver`) — drivers post their availability, current location and vehicle
  details, and see the list of pending rides.
- **Accepting a ride** (`/accept_ride/<ride_id>`) — sets the ride to `accepted`, attaches the driver,
  generates a random five-digit confirmation code, and computes an ETA.
- **ETA** — great-circle (haversine) distance between two `"lat,lng"` strings divided by a fixed
  40 km/h assumption. There is no maps/routing API; if either location fails to parse, the ETA
  falls back to the literal string `"30 min"`.
- **Customer dashboard** (`/customer`) — the user's own ride requests plus a count of available
  drivers. The flash message says drivers "will be notified", but no notification is ever sent.
- **Polling endpoint** — `GET /api/ride_status/<ride_id>` returns the ride's current status as JSON.
- **Trip page** — `/trip/<trip_id>` renders a document from the `trips` collection.

### What it does *not* do

Despite `Trip` and `Driver` model classes existing in `app/models.py`, nothing in the request flow
creates a `Trip`, completes a ride, or calculates a fare. There is no payment code, no map, no
real-time push, and no driver-matching beyond "list all pending rides to every driver".

## Tech stack

- Python 3.12, Flask (application factory in `app/__init__.py`)
- MongoDB via Flask-PyMongo — database name `ridehailing`, collections `users`, `rides`, `drivers`, `trips`
- Flask-Login (sessions), Flask-WTF + WTForms (forms and CSRF), Werkzeug (password hashing)
- Jinja2 templates, plain CSS/JS in `app/static/`

## Running it

There is **no `requirements.txt` in this repo**. Based on the imports in the source you need:

```bash
python3 -m venv venv && source venv/bin/activate
pip install Flask Flask-PyMongo Flask-Login Flask-WTF WTForms email-validator python-dotenv
```

You also need a MongoDB server listening on `localhost:27017`; the database is created on first write.

### Known problem with the entry point

The root `app.py` begins with `from . import create_app`, which is a relative import in a top-level
script. **`python app.py` therefore fails with `ImportError: attempted relative import with no known
parent package`.** Until that line is changed to `from app import create_app`, start the app through
the factory instead:

```bash
flask --app "app:create_app" run --debug
```

Then open <http://127.0.0.1:5000>.

Note that `app/__init__.py` hardcodes `SECRET_KEY = "supersecretkey"` and
`MONGO_URI = "mongodb://localhost:27017/ridehailing"` directly in the factory — the `.env` file is
loaded by `app.py` but its values are never read by the app.

## Repository hygiene

- **`.env` is committed to this public repository.** It contains M-Pesa (Daraja), PayPal and Airtel
  Money credentials and should be treated as leaked — see the security note below.
- `app/g.py` is unrelated to this project. It is a 449-line one-off code generator that scaffolds a
  different application ("geniusbabycosmetics") into a hardcoded local path. It is never imported
  and can be deleted.
- Compiled `app/__pycache__/*.pyc` files are committed. There is no `.gitignore`.

## Security

⚠️ The committed `.env` exposes live-looking payment credentials (`MPESA_CONSUMER_KEY`,
`MPESA_CONSUMER_SECRET`, `MPESA_PASSKEY`, `PAYPAL_CLIENT_SECRET`, `AIRTEL_MONEY_CLIENT_SECRET`,
`AIRTEL_MONEY_HASH_KEY`). **Rotate all of them, then remove the file from git history and add a
`.gitignore`.** None of these values are used by the ride-hailing code — they appear to have been
copied from a different project (the M-Pesa callback URL points at `online-store-soch.onrender.com`).

## Status

**Prototype.** Single commit (2025-09-07). The signup → request → accept loop is implemented; ride
completion, fares and notifications are not. The documented entry point does not run as committed.

## Licence

GPL-3.0 (see `LICENSE`).
