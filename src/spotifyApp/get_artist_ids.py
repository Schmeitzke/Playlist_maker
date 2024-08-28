import requests
import pandas as pd
import time
import base64
from tqdm import tqdm

# Spotify API credentials
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'

def get_access_token(client_id, client_secret):
    """Obtain an access token from the Spotify API using Client Credentials Flow"""
    url = 'https://accounts.spotify.com/api/token'
    
    # Encode client_id and client_secret in base64
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

def search_artist(artist_name, access_token):
    """Search for the artist on Spotify and return their Spotify ID"""
    search_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'q': artist_name,
        'type': 'artist',
        'limit': 1  # We only need the top result
    }
    
    response = requests.get(search_url, headers=headers, params=params)
    
    if response.status_code == 200:
        results = response.json()
        if results['artists']['items']:
            artist = results['artists']['items'][0]
            return artist['id']  
        else:
            return None  # No match found
    else:
        print(f"Error searching for {artist_name}: {response.status_code} {response.text}")
        return None

def retrieve_and_save_artist_ids(input_file, output_file, access_token):
    """Retrieve Spotify IDs for all artists and save them to a new CSV file"""
    artist_df = pd.read_csv(input_file)
    
    artist_df['Spotify ID'] = None
    
    for index, row in tqdm(artist_df.iterrows(), total=artist_df.shape[0], desc="Processing Artists", unit="artist"):
        artist_name = row['Artist Name']
        artist_id = search_artist(artist_name, access_token)
        
        if artist_id:
            artist_df.at[index, 'Spotify ID'] = artist_id
        
        # Respect Spotify rate limits by waiting between requests
        time.sleep(1)
    
    artist_df.to_csv(output_file, index=False)
    print(f"Saved updated artist data with Spotify IDs to {output_file}")

def main():
    input_file = 'artist_names.csv'  
    output_file = 'artist_names_ids.csv'
    
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    
    retrieve_and_save_artist_ids(input_file, output_file, access_token)

if __name__ == "__main__":
    main()
