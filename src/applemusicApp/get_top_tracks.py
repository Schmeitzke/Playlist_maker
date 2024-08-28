import requests
import pandas as pd
import jwt
import time
from tqdm import tqdm

# Apple Music API credentials
TEAM_ID = 'YOUR_TEAM_ID'
KEY_ID = 'YOUR_KEY_ID'
PRIVATE_KEY = '''
-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----
'''

def generate_token():
    """Generate a JWT token for Apple Music API authentication"""
    token = jwt.encode({
        'iss': TEAM_ID,
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600  # Token expires in 1 hour
    }, PRIVATE_KEY, algorithm='ES256', headers={
        'kid': KEY_ID
    })
    return token

def get_top_tracks(artist_id, token, limit=10):
    """Get the top tracks for an artist by their Apple Music ID"""
    url = f'https://api.music.apple.com/v1/catalog/us/artists/{artist_id}/songs'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'limit': limit,
        'sort': 'popularity'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Failed to retrieve top tracks for artist ID {artist_id}: {response.status_code} {response.text}")
        return []

def retrieve_top_tracks(input_file, output_file, token):
    """Retrieve the top tracks for artists and save them to a new CSV file"""
    artist_df = pd.read_csv(input_file)
    
    top_tracks_data = []

    for index, row in tqdm(artist_df.iterrows(), total=artist_df.shape[0], desc="Processing Artists", unit="artist"):
        artist_name = row['Artist Name']
        artist_id = row['Apple Music ID']
        
        if pd.isna(artist_id):
            continue  # Skip artists without an Apple Music ID
        
        top_tracks = get_top_tracks(artist_id, token)
        
        for track in top_tracks:
            track_info = {
                'Artist Name': artist_name,
                'Apple Music Artist ID': artist_id,
                'Track Name': track['attributes']['name'],
                'Track Apple Music ID': track['id'],
                'Album Name': track['attributes']['albumName'],
                'Preview URL': track['attributes'].get('previews', [{}])[0].get('url')
            }
            top_tracks_data.append(track_info)
        
        time.sleep(1)  # Respect API rate limits
    
    top_tracks_df = pd.DataFrame(top_tracks_data)
    top_tracks_df.to_csv(output_file, index=False)
    print(f"Saved top tracks data to {output_file}")

def main():
    input_file = 'artist_names_ids_apple_music.csv'
    output_file = 'artist_top_tracks_apple_music.csv'
    
    token = generate_token()
    
    retrieve_top_tracks(input_file, output_file, token)

if __name__ == "__main__":
    main()