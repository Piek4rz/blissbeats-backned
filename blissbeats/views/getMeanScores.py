import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
import time
import math
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlist_ids = [
    'https://open.spotify.com/playlist/37i9dQZF1DWURfu7Lk3xJ1?si=87906d254b57483a',
    'https://open.spotify.com/playlist/37i9dQZF1DWXXRO8Hsxc4q?si=b95dd11c907c4d20',
    'https://open.spotify.com/playlist/37i9dQZF1DWZqd5JICZI0u?si=6d72aa35d29b4de0'
]
sleep_time = 2
audio_features = []

for playlist_id in playlist_ids:
    print("now processing: " + playlist_id)
    results_items = sp.playlist_items(playlist_id)
    all_tracks_number = results_items['total']
    i = math.ceil(all_tracks_number / 100)

    for j in range(i):
        results_items = sp.playlist_items(playlist_id, offset=j * 100)
        batch = [item['track']['id'] for item in results_items['items'] if
                 item['track'] is not None and item['track']['id'] is not None]
        features = sp.audio_features(batch)
        audio_features.extend(features)
        time.sleep(sleep_time)
        print("tracks processed: " + str(j * 100) + " / " + str(all_tracks_number))

mean_features = {}
for feature in ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness',
                'tempo', 'valence']:
    feature_values = [track[feature] for track in audio_features if track is not None and track[feature] is not None]
    mean_features[feature] = np.mean(feature_values)

# # print(audio_features)
# print(mean_features)
