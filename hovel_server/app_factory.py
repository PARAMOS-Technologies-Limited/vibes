from flask import Flask
from flask_cors import CORS
from .config import configure_app
from .logging_config import configure_logging
from .api import register_blueprints
from .middleware import setup_middleware

def create_app():
    configure_logging()
    app = Flask(__name__)
    configure_app(app)
    CORS(app)
    register_blueprints(app)
    setup_middleware(app)
    return app 