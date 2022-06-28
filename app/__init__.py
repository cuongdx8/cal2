from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify
from sqlalchemy.orm import declarative_base

app = Flask(__name__)
swagger = Swagger(app)
Base = declarative_base()

load_dotenv()

from app.auth.auth_routes import bp_auth

app.register_blueprint(bp_auth)
