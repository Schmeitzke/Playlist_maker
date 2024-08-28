# Music Playlist Generator

This project allows you to create playlists on both Apple Music and Spotify based on a list of artists. It consists of several Python scripts and bash scripts to run them all together for each platform.

## Prerequisites

1. Python 3.7 or higher
2. pip (Python package manager)
3. For Apple Music:
   - An Apple Developer account (requires a $99/year subscription)
   - A MusicKit key from Apple
4. For Spotify:
   - A Spotify Developer account (free)
   - A Spotify application with Client ID and Client Secret

## Setup

### Apple Music Setup

1. Sign up for an Apple Developer account at [developer.apple.com](https://developer.apple.com).
2. Once your account is set up, go to the Certificates, Identifiers & Profiles section.
3. Create a new MusicKit key:
   - Go to "Keys" and click the "+" button.
   - Select "MusicKit" and configure your key.
   - Download the key file (.p8) and note down the Key ID.

4. Update Credentials:
   In each of the Apple Music Python scripts (`get_artist_ids.py`, `get_top_tracks.py`, and `make_playlist.py`), update the following global variables:

   ```python
   TEAM_ID = 'YOUR_TEAM_ID'  # Your Apple Developer Team ID
   KEY_ID = 'YOUR_KEY_ID'  # The Key ID of your MusicKit key
   PRIVATE_KEY = '''
   -----BEGIN PRIVATE KEY-----
   YOUR_PRIVATE_KEY_HERE
   -----END PRIVATE KEY-----
   '''  # The content of your .p8 key file
   ```

   In `make_playlist.py`, also update:

   ```python
   PLAYLIST_NAME = 'YOUR_PLAYLIST_NAME'  # The name you want for your playlist
   ```

### Spotify Setup

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and log in or create an account.
2. Create a new application and note down the Client ID and Client Secret.
3. In your application settings, add `http://localhost:3000/callback` as a Redirect URI.
4. Update Credentials:
   In each of the Spotify Python scripts (`get_artist_ids.py`, `get_top_tracks.py`, and `make_playlist.py`), update the following global variables:

   ```python
   CLIENT_ID = 'YOUR_CLIENT_ID'
   CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
   ```

   In `make_playlist.py`, also update:

   ```python
   USER_ID = 'USER_ID'  # Your Spotify user ID
   PLAYLIST_NAME = 'YOUR_PLAYLIST_NAME'
   PUBLIC_PLAYLIST = False  # Set to True if you want the playlist to be public
   ```

### Common Setup Steps

1. Create Artist Scraper:
   Create a Python script to scrape artist names and save them to a CSV file named `artist_names.csv`. Place this script in the `src/artistScrapers` folder. The CSV should have a column named "Artist Name".

2. Update Bash Scripts:
   Open `run_applemusicApp.sh` and `run_spotifyApp.sh` and ensure that the line calling your scraper script is correct:

   ```bash
   $PYTHON_EXECUTABLE yourscraperscript.py
   ```

   Replace `yourscraperscript.py` with the actual name of your scraper script.

3. Install Dependencies:
   Ensure you have a `requirements.txt` file in the parent directory of `src` with the following content:

   ```
   requests
   pandas
   pyjwt
   flask
   tqdm
   ```

## Running the Scripts

1. Open a terminal and navigate to the directory containing the bash scripts.
2. Make the scripts executable (if not already):
   ```
   chmod +x run_applemusicApp.sh run_spotifyApp.sh
   ```
3. Run the desired script:\
   For Apple Music:
   ```
   ./run_applemusicApp.sh
   ```
   For Spotify:
   ```
   ./run_spotifyApp.sh
   ```

This will:
- Install required packages
- Run your artist scraper
- Get artist IDs for the respective platform
- Get top tracks for each artist
- Create a playlist with these tracks

When `make_playlist.py` runs for either platform, it will open a web browser for you to authorize the application. Follow the prompts to give the necessary permissions.

## Troubleshooting

- If you encounter permission issues, ensure your developer accounts are active and your API keys are properly set up.
- If tracks aren't being added to the playlist, check that your scraper is producing valid artist names and that these artists are available on the respective platform.
- For any API errors, check the error messages in the console output for more details.

## Notes

- Both Apple Music and Spotify APIs have rate limits. The scripts include pauses to respect these limits, but you may need to adjust if you're processing a large number of artists.
- Ensure your developer accounts remain active to maintain API access.
- Always keep your API credentials secure and never share them publicly.
- The Spotify implementation uses the Authorization Code flow, which requires user interaction to grant permissions. Make sure you're logged into the correct Spotify account when authorizing.

## Differences Between Apple Music and Spotify Implementations

1. Authentication:
   - Apple Music uses a MusicKit key and JWT for authentication.
   - Spotify uses OAuth 2.0 with the Authorization Code flow.

2. User Interaction:
   - Apple Music may require less user interaction after initial setup.
   - Spotify requires the user to grant permissions through a web browser for each playlist creation.

3. Playlist Creation:
   - Apple Music allows direct playlist creation with the provided credentials.
   - Spotify requires user-specific authentication to create playlists on the user's account.

4. API Endpoints:
   - The scripts use different API endpoints and parameters for each platform.

5. Rate Limiting:
   - Both platforms have rate limits, but they may differ in specifics. Adjust wait times if necessary.

Choose the appropriate script based on your preferred music platform and ensure you have the correct credentials set up for each.