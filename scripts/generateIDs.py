import requests
import base64
import pandas as pd

# Your Spotify Developer credentials
CLIENT_ID = 'client_id'
CLIENT_SECRET = 'client_secret'

# Get an access token
def get_access_token(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}"
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    return response.json().get("access_token")

# Get track and artist ID from Spotify
def get_track_and_artist_id(track_name, artist_name, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    query = f"track:{track_name} artist:{artist_name}"
    params = {
        "q": query,
        "type": "track",
        "limit": 1
    }

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    results = response.json()
    items = results.get("tracks", {}).get("items", [])
    if items:
        track_id = items[0]["id"]
        artist_id = items[0]["artists"][0]["id"]  # first listed artist
        return track_id, artist_id
    else:
        return None, None

# Load your CSV
df = pd.read_csv("data/StreamingHistory_music_transformed.csv")

# Get access token
token = get_access_token(CLIENT_ID, CLIENT_SECRET)

# Collect IDs
spotify_track_ids = []
spotify_artist_ids = []

for index, row in df.iterrows():
    track = row["trackName"]
    artist = row["artistName"]
    track_id, artist_id = get_track_and_artist_id(track, artist, token)
    spotify_track_ids.append(track_id)
    spotify_artist_ids.append(artist_id)

# Add to DataFrame
df["spotifyTrackId"] = spotify_track_ids
df["spotifyArtistId"] = spotify_artist_ids

# Save result
df.to_csv("data/StreamingHistory_music.csv", index=False)
