from flask import Flask
import secrets

def create_app():
    app = Flask(__name__)
    # Generate a random secret key
    app.secret_key = secrets.token_hex(16)
    return app