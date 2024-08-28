import requests
import pandas as pd
import base64
import time
from tqdm import tqdm
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from flask import Flask, request, redirect

# Spotify API credentials
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'http://localhost:3000/callback'
SCOPE = 'playlist-modify-public playlist-modify-private'
USER_ID = 'USER_ID'  # Your Spotify user ID
PLAYLIST_NAME = 'YOUR_PLAYLIST_NAME'
PUBLIC_PLAYLIST = False

app = Flask(__name__)

def get_auth_url(client_id, redirect_uri, scope):
    """Generate the Spotify authorization URL."""
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope,
    }
    return f"https://accounts.spotify.com/authorize?{urlencode(params)}"

def get_tokens(auth_code, client_id, client_secret, redirect_uri):
    """Exchange authorization code for access and refresh tokens."""
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve tokens: {response.status_code} {response.text}")

def refresh_access_token(refresh_token, client_id, client_secret):
    """Refresh the access token using the refresh token."""
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to refresh access token: {response.status_code} {response.text}")

def create_playlist(user_id, access_token, playlist_name=PLAYLIST_NAME, description="Playlist created using Spotify API", public=PUBLIC_PLAYLIST):
    """Create a new Spotify playlist for the user."""
    url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "name": playlist_name,
        "description": description,
        "public": public
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        playlist_id = response.json()['id']
        print(f"Playlist '{playlist_name}' created successfully with ID: {playlist_id}")
        return playlist_id
    else:
        raise Exception(f"Failed to create playlist: {response.status_code} {response.text}")

def add_tracks_to_playlist(playlist_id, track_uris, access_token):
    """Add tracks to a Spotify playlist."""
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "uris": track_uris
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        snapshot_id = response.json()['snapshot_id']
    else:
        raise Exception(f"Failed to add tracks to playlist: {response.status_code} {response.text}")

@app.route('/callback')
def callback():
    """Handle the redirect from Spotify after authorization."""
    code = request.args.get('code')
    tokens = get_tokens(code, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    access_token = tokens['access_token']

    playlist_id = create_playlist(USER_ID, access_token)

    tracks_df = pd.read_csv('artist_top_tracks.csv')
    track_uris = tracks_df['Track Spotify ID'].apply(lambda x: f"spotify:track:{x}").tolist()

    for i in tqdm(range(0, len(track_uris), 100), desc="Adding tracks to playlist", unit="tracks"):
        batch = track_uris[i:i+100]
        add_tracks_to_playlist(playlist_id, batch, access_token)
        time.sleep(1)  # Pause to respect rate limits

    return "Playlist created and tracks added successfully!"

def main():
    auth_url = get_auth_url(CLIENT_ID, REDIRECT_URI, SCOPE)
    print("Please go to the following URL to authorize the app:")
    print(auth_url)
    webbrowser.open(auth_url)
    app.run(port=3000)

if __name__ == "__main__":
    main()
