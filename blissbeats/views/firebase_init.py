import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('blissbeats-9d6b0-firebase-adminsdk-p2jm4-65004bb384.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
