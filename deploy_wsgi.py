"""Deployment entrypoint for mpikipiki.

`python app.py` fails: app.py uses a relative import (`from . import
create_app`) while being run as a top-level script. Rather than patching it,
this file reaches the factory the way Flask does (`flask --app "app:create_app"`
resolves the *package* app/, not app.py — packages shadow same-named modules).

It is additive only. app/__init__.py is untouched. It:

  * builds the app through create_app(),
  * repoints the Mongo connection and the session secret at environment
    variables (both are hardcoded literals in app/__init__.py),
  * registers a /healthz probe.

Run with:  gunicorn deploy_wsgi:app
"""

import os

from pymongo import MongoClient

from app import create_app, mongo  # noqa: E402  (the package, not app.py)

app = create_app()

# --- secret key -------------------------------------------------------------
# app/__init__.py sets app.config["SECRET_KEY"] = "supersecretkey" with a
# "replace with env var in production" comment. This is that replacement.
_secret = os.environ.get("SECRET_KEY")
if _secret:
    app.secret_key = _secret
    app.config["SECRET_KEY"] = _secret

# --- MongoDB ----------------------------------------------------------------
# app/__init__.py hardcodes MONGO_URI = "mongodb://localhost:27017/ridehailing"
# and mongo.init_app(app) has already run by the time we get here. flask_pymongo
# keeps `cx` (client) and `db` (database) as plain attributes, and every call
# site uses `mongo.db.<collection>`, so rebinding those two attributes is enough
# and does not depend on init_app being re-entrant.
_uri = os.environ.get("MONGO_URI")
if _uri:
    app.config["MONGO_URI"] = _uri
    _client = MongoClient(_uri)
    _db = _client.get_default_database()
    if _db is None:
        raise RuntimeError(
            "MONGO_URI must include a database name, e.g. "
            "mongodb://host:27017/ridehailing"
        )
    mongo.cx = _client
    mongo.db = _db

# --- health probe -----------------------------------------------------------
if "healthz" not in app.view_functions:

    @app.route("/healthz")
    def healthz():
        """Liveness probe. No DB round trip: this answers 'is the worker
        alive', not 'is MongoDB up'."""
        return {"status": "ok"}, 200


if __name__ == "__main__":  # pragma: no cover - local smoke test only
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5759)))
