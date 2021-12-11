import os
from datetime import timedelta


class Config:
    CORS_HEADERS = ['Content-Type','Authorization']
    MAX_CONTENT_LENGTH = 30 * 1024 * 1024
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'anything but string'
    # MONOGO_URI = 'mongodb://localhost:27017/4kdevelopment'
    MONOGO_URI = "mongodb+srv://abel:test@cluster0.nhd1d.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    CV_PATH = './cv'
    PROFILE_PICTURES = './profile'
    THUMBNAILS = './thumbnails'
    EVENTS = './events'
    ALLOWED_EXTENSIONS = {'pdf','docs','doc','rtf'}
    # jwt configuration
    JWT_TOKEN_LOCATION = "headers"
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY') or 'anything but string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # google auth
    # CLIENT_ID = "475271500037-5gg9viio8pftqjs1ra3aq9f3ss8f0nru.apps.googleusercontent.com"
    CLIENT_ID = "843154350382-qvjkg63v1m17g3tp722e5va4v77o011h.apps.googleusercontent.com"

class development_config(Config):
    DEBUG=True

class production_config(Config):
     MONOGO_URI = 'mongodb://localhost:27017/4kproduction'

configuration = {
    'development':development_config,
    'production':production_config,
    'default':development_config
}
