import math
import time

from flask import request, jsonify, Blueprint
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .spotify_auth import CLIENT_ID, CLIENT_SECRET
from .scores import scores
from numpy import dot
from numpy.linalg import norm

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

spotify_user_data_bp = Blueprint('spotify__user_data', __name__)

audio_features = []


def fetch_playlist_library():
    playlist_ids = [
        'https://open.spotify.com/playlist/29NKUr4tt9VgG7izd5eD4g?si=8bcf5cb4b4954f03'
    ]
    sleep_time = 1
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

    print("tracks processed: " + str(len(audio_features)) + " / " + str(len(audio_features)))


def calculate_user_scores(user_answers, scores):
    final_scores = {
        "acousticness": 0,
        "danceability": 0,
        "energy": 0,
        "instrumentalness": 0,
        "liveness": 0,
        "loudness": 0,
        "speechiness": 0,
        "tempo": 0,
        "valence": 0
    }

    total_answers = 0
    for answers in user_answers:
        for answer in answers:
            question = answer['question']
            user_response = answer['answer']
            if question == "mood":
                print(question)
                print(user_response)
                mood_score = int(user_response)
                mood_score = (mood_score - 1) / 9
                for feature in final_scores:
                    sad_score = scores['mood']['sad'][feature]
                    happy_score = scores['mood']['happy'][feature]
                    mood_adjusted_score = sad_score + mood_score * (happy_score - sad_score)
                    print(mood_adjusted_score)
                    final_scores[feature] += mood_adjusted_score
                total_answers += 1
            elif question in scores and user_response in scores[question]:
                print(question)
                print(user_response)
                for feature, value in scores[question][user_response].items():
                    if feature in final_scores:
                        final_scores[feature] += value
                total_answers += 1

    for feature in final_scores:
        final_scores[feature] /= total_answers
    print(final_scores)
    return final_scores


def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))


def recommend_songs(user_responses, library, user_time_preference):
    time_options = {
        "< 30 min": 25 * 60 * 1000,
        "30-60 min": 45 * 60 * 1000,
        "1-2 hours": 90 * 60 * 1000,
        "> 2 hours": 145 * 60 * 1000
    }

    duration_ms = time_options.get(user_time_preference, 30 * 60 * 1000)
    total_duration = 0
    recommended_songs = []

    similarity_scores = []

    for song in library:
        if song is not None:
            song_features = [song[feature] for feature in user_responses.keys() if
                             feature is not None and feature in song]
            if len(song_features) == len(user_responses):
                similarity = cosine_similarity(list(user_responses.values()), song_features)
                similarity_scores.append((song, similarity))

    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    for song, similarity in similarity_scores:
        if total_duration + song['duration_ms'] <= duration_ms:
            recommended_songs.append(song['uri'])
            total_duration += song['duration_ms']
        else:
            break

    return recommended_songs


@spotify_user_data_bp.route('/submit_answers', methods=['POST'])
def submit():
    responses = request.get_json()
    print(responses)
    # print(scores)
    # print(audio_features)
    flattened_responses = [item for sublist in responses for item in sublist]
    time_preference = next(
        (response['answer'] for response in flattened_responses if response['question'] == 'duration'),
        "< 30 min")

    user_scores = calculate_user_scores(responses, scores)
    recommended_songs = recommend_songs(user_scores, audio_features, time_preference)
    # print(recommended_songs)
    return jsonify({'uris': recommended_songs}), 200
