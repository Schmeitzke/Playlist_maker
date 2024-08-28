import requests
import pandas as pd
import time
import base64
from tqdm import tqdm

# Step 1: Set up your Spotify API credentials
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
MARKET = 'YOUR_COUNTRY_CODE'  # Market for top tracks, e.g., 'US' (PAY ATTENTION, spotify is not available in all countries and thus not all countries have an available market)

def get_access_token(client_id, client_secret):
    """Obtain an access token from the Spotify API using Client Credentials Flow"""
    url = 'https://accounts.spotify.com/api/token'
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {
        'Authorization': f'Basic {b64_auth_str}'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token']
    else:
        raise Exception(f"Failed to get access token: {response.status_code} {response.text}")

def get_top_tracks(artist_id, access_token, market=MARKET):
    """Get the top tracks for an artist by their Spotify ID"""
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'market': market
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()['tracks']
    else:
        print(f"Failed to retrieve top tracks for artist ID {artist_id}: {response.status_code} {response.text}")
        return []

def retrieve_top_tracks(input_file, output_file, access_token, market=MARKET):
    """Retrieve the top tracks for artists and save them to a new CSV file"""
    artist_df = pd.read_csv(input_file)
    
    top_tracks_data = []

    for _, row in tqdm(artist_df.iterrows(), total=artist_df.shape[0], desc="Processing Artists", unit="artist"):
        artist_name = row['Artist Name']
        artist_id = row['Spotify ID']
        
        if pd.isna(artist_id):
            continue  # Skip artists without a Spotify ID
        
        top_tracks = get_top_tracks(artist_id, access_token, market)
        
        for track in top_tracks:
            track_info = {
                'Artist Name': artist_name,
                'Spotify Artist ID': artist_id,
                'Track Name': track['name'],
                'Track Spotify ID': track['id'],
                'Album Name': track['album']['name'],
                'Track Popularity': track['popularity'],
                'Preview URL': track['preview_url']
            }
            top_tracks_data.append(track_info)
        
        # Respect Spotify rate limits by waiting between requests
        time.sleep(1)
    
    top_tracks_df = pd.DataFrame(top_tracks_data)
    top_tracks_df.to_csv(output_file, index=False)
    print(f"Saved top tracks data to {output_file}")

def main():
    input_file = 'artist_names_ids.csv'  
    output_file = 'artist_top_tracks.csv'  
    
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    
    retrieve_top_tracks(input_file, output_file, access_token)

if __name__ == "__main__":
    main()
