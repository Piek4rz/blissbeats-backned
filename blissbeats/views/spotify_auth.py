import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, redirect
import requests
from .firebase_init import db

load_dotenv()

spotify_auth_bp = Blueprint('spotify_auth', __name__)

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
REDIRECT_URI = 'http://localhost:3000/dashboard'
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')


@spotify_auth_bp.route('/login', methods=['GET'])
def spotify_login():
    return redirect(
        f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=user-read-private%20user-read-email%20playlist-modify-private%20playlist-modify-public%20"
    )


@spotify_auth_bp.route('/callback', methods=['GET'])
def spotify_callback():
    auth_code = request.args.get('code')
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    access_token = response.json().get('access_token')
    refresh_token = response.json().get('refresh_token')
    user_id = request.args.get('currentUser')
    doc_ref = db.collection('SpotifyAccounts').document(user_id)
    doc_ref.set({
        'refresh_token': refresh_token
    })

    return jsonify({'access_token': access_token})


@spotify_auth_bp.route('/refresh_token', methods=['POST'])
def refresh_token():
    user_id = request.json.get('user_id')
    doc_ref = db.collection('SpotifyAccounts').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        refresh_token = doc.to_dict().get('refresh_token')
    else:
        return jsonify({'error': 'User not found'}), 404

    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })

    if response.status_code != 200:
        return jsonify({'error': 'Failed to refresh access token'}), 400

    access_token = response.json().get('access_token')
    expires_in = response.json().get('expires_in')

    return jsonify({'access_token': access_token, 'expires_in': expires_in})
