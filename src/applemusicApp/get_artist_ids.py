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

def search_artist(artist_name, token):
    """Search for the artist on Apple Music and return their Apple Music ID"""
    search_url = 'https://api.music.apple.com/v1/catalog/us/search'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'term': artist_name,
        'types': 'artists',
        'limit': 1
    }
    
    response = requests.get(search_url, headers=headers, params=params)
    
    if response.status_code == 200:
        results = response.json()
        if results['results'].get('artists'):
            artist = results['results']['artists']['data'][0]
            return artist['id']  # Return Apple Music ID
        else:
            return None  # No match found
    else:
        print(f"Error searching for {artist_name}: {response.status_code} {response.text}")
        return None

def retrieve_and_save_artist_ids(input_file, output_file, token):
    """Retrieve Apple Music IDs for all artists and save them to a new CSV file"""
    artist_df = pd.read_csv(input_file)
    
    artist_df['Apple Music ID'] = None
    
    for index, row in tqdm(artist_df.iterrows(), total=artist_df.shape[0], desc="Processing Artists", unit="artist"):
        artist_name = row['Artist Name']
        artist_id = search_artist(artist_name, token)
        
        if artist_id:
            artist_df.at[index, 'Apple Music ID'] = artist_id
        
        time.sleep(1)  # Respect API rate limits
    
    artist_df.to_csv(output_file, index=False)
    print(f"Saved updated artist data with Apple Music IDs to {output_file}")

def main():
    input_file = 'artist_names.csv'
    output_file = 'artist_names_ids_apple_music.csv'
    
    token = generate_token()
    
    retrieve_and_save_artist_ids(input_file, output_file, token)

if __name__ == "__main__":
    main()