from flask import Flask, g
from .app_factory import create_app
from .db_connect import close_db, get_db

app = create_app()  # No need to pass the secret key

# Register Blueprints
from app.blueprints.sales import sales
app.register_blueprint(sales)

from app.blueprints.regions import regions
app.register_blueprint(regions)

from . import routes

@app.before_request
def before_request():
    g.db = get_db()

# Setup database connection teardown
@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)