import requests
import pandas as pd
import jwt
import time
from tqdm import tqdm
import webbrowser
from urllib.parse import urlencode
from flask import Flask, request

app = Flask(__name__)

# Apple Music API credentials
TEAM_ID = 'YOUR_TEAM_ID'
KEY_ID = 'YOUR_KEY_ID'
PRIVATE_KEY = '''
-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----
'''
REDIRECT_URI = 'http://localhost:3000/callback'
PLAYLIST_NAME = 'YOUR_PLAYLIST_NAME'

def generate_developer_token():
    """Generate a JWT token for Apple Music API authentication"""
    token = jwt.encode({
        'iss': TEAM_ID,
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600  # Token expires in 1 hour
    }, PRIVATE_KEY, algorithm='ES256', headers={
        'kid': KEY_ID
    })
    return token

def get_auth_url():
    """Generate the Apple Music authorization URL."""
    params = {
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'client_id': KEY_ID,
        'scope': 'playlist-modify'
    }
    return f"https://appleid.apple.com/auth/authorize?{urlencode(params)}"

def get_user_token(auth_code):
    """Exchange authorization code for a user token."""
    url = 'https://appleid.apple.com/auth/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': KEY_ID,
        'client_secret': generate_developer_token(),
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to retrieve user token: {response.status_code} {response.text}")

def create_playlist(user_token, developer_token, playlist_name=PLAYLIST_NAME, description="Playlist created using Apple Music API"):
    """Create a new Apple Music playlist for the user."""
    url = 'https://api.music.apple.com/v1/me/library/playlists'
    headers = {
        'Authorization': f'Bearer {developer_token}',
        'Music-User-Token': user_token,
        'Content-Type': 'application/json'
    }
    payload = {
        "attributes": {
            "name": playlist_name,
            "description": description
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        playlist_id = response.json()['data'][0]['id']
        print(f"Playlist '{playlist_name}' created successfully with ID: {playlist_id}")
        return playlist_id
    else:
        raise Exception(f"Failed to create playlist: {response.status_code} {response.text}")

def add_tracks_to_playlist(playlist_id, track_ids, user_token, developer_token):
    """Add tracks to an Apple Music playlist."""
    url = f'https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks'
    headers = {
        'Authorization': f'Bearer {developer_token}',
        'Music-User-Token': user_token,
        'Content-Type': 'application/json'
    }
    payload = {
        "data": [{"id": track_id, "type": "songs"} for track_id in track_ids]
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 204:
        print(f"Successfully added {len(track_ids)} tracks to the playlist.")
    else:
        raise Exception(f"Failed to add tracks to playlist: {response.status_code} {response.text}")

@app.route('/callback')
def callback():
    """Handle the redirect from Apple Music after authorization."""
    code = request.args.get('code')
    user_token = get_user_token(code)
    developer_token = generate_developer_token()

    # Create a new playlist
    playlist_id = create_playlist(user_token, developer_token)

    # Load track IDs from the CSV file
    tracks_df = pd.read_csv('artist_top_tracks_apple_music.csv')
    track_ids = tracks_df['Track Apple Music ID'].tolist()

    # Add tracks to the playlist in batches of 100 (Apple Music API limit)
    for i in tqdm(range(0, len(track_ids), 100), desc="Adding tracks to playlist", unit="tracks"):
        batch = track_ids[i:i+100]
        add_tracks_to_playlist(playlist_id, batch, user_token, developer_token)
        time.sleep(1)  # Pause to respect rate limits

    return "Playlist created and tracks added successfully!"

def main():
    auth_url = get_auth_url()
    print("Please go to the following URL to authorize the app:")
    print(auth_url)
    webbrowser.open(auth_url)
    app.run(port=3000)

if __name__ == "__main__":
    main()