import logging

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify
from sqlalchemy.orm import declarative_base

app = Flask(__name__)
swagger = Swagger(app)
Base = declarative_base()

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from app.auth.auth_routes import bp_auth

app.register_blueprint(bp_auth)

from app.connection.connection_routes import bp_connection

app.register_blueprint(bp_connection)

from app.calendar.calendar_routes import bp_calendar

app.register_blueprint(bp_calendar)

from app.event.event_routes import bp_event

app.register_blueprint(bp_event)