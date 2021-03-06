from flask import Flask,redirect,url_for,render_template,request
from flask_pymongo import PyMongo
from flask_cors import CORS
from config import Config,configuration
from flask_jwt_extended import create_access_token,get_jwt,jwt_required,JWTManager,create_refresh_token,verify_jwt_in_request      
import os


# import firebase admin and initialize the cred file
import firebase_admin
from firebase_admin import credentials,auth
# path of the json file 
filename = "k-lab-317405-firebase-adminsdk-wzb86-edaa1008dc.json";
cred = credentials.Certificate(filename)

default_app = firebase_admin.initialize_app(cred)


#  Add Cors and pyjwt

mongo = PyMongo()
db = mongo.db

app = Flask(__name__)
jwt = JWTManager(app)

def create_app(config_name):
    app.config.from_object(configuration[config_name])
    mongo.init_app(app,uri=configuration[config_name].MONOGO_URI)
    cors = CORS(app, resources={r"*": {"origins": "*"}},supports_credentials=True)
    from .api_v1 import api_v1
    from .web import web
    app.register_blueprint(api_v1)
    app.register_blueprint(web)
    return app