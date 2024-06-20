import math
import time
import os
from dotenv import load_dotenv
import spotipy
from flask import Flask
from flask_cors import CORS
from spotipy import SpotifyClientCredentials

load_dotenv()

from blissBeats.views.spotify_auth import spotify_auth_bp
from blissBeats.views.spotify_user_data import spotify_user_data_bp, fetch_playlist_library

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def create_app():
    app = Flask(__name__)
    CORS(app, origins='http://localhost:3000')

    app.register_blueprint(spotify_auth_bp)
    app.register_blueprint(spotify_user_data_bp)
    fetch_playlist_library()

    return app
