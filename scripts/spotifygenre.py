import pandas as pd
import requests
import json
import time
from typing import Dict, List, Optional
import os
from base64 import b64encode

class SpotifyGenreFetcher:
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the Spotify API client with credentials.
        
        Args:
            client_id: Your Spotify App Client ID
            client_secret: Your Spotify App Client Secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.artist_cache = {}
        self.cache_file = "data/artist_genre_cache.json"
        
        # Load existing cache if it exists
        self.load_cache()
        
        # Get initial access token
        self.get_access_token()
    
    def load_cache(self):
        """Load artist genre cache from file if it exists."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.artist_cache = json.load(f)
                print(f"Loaded {len(self.artist_cache)} artists from cache")
            except Exception as e:
                print(f"Error loading cache: {e}")
                self.artist_cache = {}
    
    def save_cache(self):
        """Save artist genre cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.artist_cache, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.artist_cache)} artists to cache")
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def get_access_token(self):
        """Get Spotify API access token using Client Credentials flow."""
        auth_url = "https://accounts.spotify.com/api/token"
        
        # Encode client credentials
        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_b64 = b64encode(client_creds.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {client_creds_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        response = requests.post(auth_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            print("Successfully obtained Spotify access token")
        else:
            raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")
    
    def get_artist_by_id(self, artist_id: str) -> Optional[Dict]:
        """
        Get artist information directly by Spotify Artist ID.
        
        Args:
            artist_id: Spotify Artist ID
            
        Returns:
            Dictionary with artist data or None if not found
        """
        if not self.access_token:
            self.get_access_token()
        
        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            response = requests.get(artist_url, headers=headers)
            
            if response.status_code == 401:  # Token expired
                print("Access token expired, getting new one...")
                self.get_access_token()
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = requests.get(artist_url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting artist {artist_id}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception while getting artist {artist_id}: {e}")
            return None
    
    def get_multiple_artists(self, artist_ids: List[str]) -> Dict[str, Dict]:
        """
        Get multiple artists in a single API call (more efficient).
        
        Args:
            artist_ids: List of Spotify Artist IDs (max 50 per call)
            
        Returns:
            Dictionary mapping artist_id to artist data
        """
        if not self.access_token:
            self.get_access_token()
        
        # Spotify API allows max 50 artists per request
        if len(artist_ids) > 50:
            raise ValueError("Maximum 50 artist IDs per request")
        
        artists_url = "https://api.spotify.com/v1/artists"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        params = {
            "ids": ",".join(artist_ids)
        }
        
        try:
            response = requests.get(artists_url, headers=headers, params=params)
            
            if response.status_code == 401:  # Token expired
                print("Access token expired, getting new one...")
                self.get_access_token()
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = requests.get(artists_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                result = {}
                for artist in data.get("artists", []):
                    if artist:  # artist could be None if ID not found
                        result[artist["id"]] = artist
                return result
            else:
                print(f"Error getting artists: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Exception while getting artists: {e}")
            return {}
    
    def get_artist_genres_by_id(self, artist_id: str, artist_name: str = None) -> Dict:
        """
        Get genres for an artist by ID, using cache if available.
        
        Args:
            artist_id: Spotify Artist ID
            artist_name: Artist name for display purposes
            
        Returns:
            Dictionary with genres and artist info
        """
        # Check cache first (using artist_id as key)
        if artist_id in self.artist_cache:
            return self.artist_cache[artist_id]
        
        # Get artist data from Spotify API
        print(f"Fetching data for artist ID: {artist_id}" + (f" ({artist_name})" if artist_name else ""))
        artist_data = self.get_artist_by_id(artist_id)
        
        result = {
            'artist_id': artist_id,
            'artist_name': '',
            'genres': [],
            'popularity': 0,
            'followers': 0,
            'found': False
        }
        
        if artist_data:
            result.update({
                'artist_name': artist_data.get("name", ""),
                'genres': artist_data.get("genres", []),
                'popularity': artist_data.get("popularity", 0),
                'followers': artist_data.get("followers", {}).get("total", 0),
                'found': True
            })
        
        # Cache the result
        self.artist_cache[artist_id] = result
        return result
    
    def process_csv_with_ids(self, input_file: str, output_file: str = None, 
                           artist_id_column: str = "spotifyArtistId", 
                           artist_name_column: str = "artistname"):
        """
        Process CSV file to add genres using Spotify Artist IDs.
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
            artist_id_column: Name of the column containing Spotify Artist IDs
            artist_name_column: Name of the column containing artist names (for display)
        """
        # Read CSV
        df = pd.read_csv(input_file)
        
        # Validate columns
        if artist_id_column not in df.columns:
            raise ValueError(f"Column '{artist_id_column}' not found. Available: {list(df.columns)}")
        
        # Get unique artist IDs to minimize API calls
        unique_artist_ids = df[artist_id_column].dropna().unique()
        print(f"Found {len(unique_artist_ids)} unique artist IDs")
        
        # Process artists in batches of 50 (Spotify API limit)
        batch_size = 50
        artist_data = {}
        
        for i in range(0, len(unique_artist_ids), batch_size):
            batch = unique_artist_ids[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}: {len(batch)} artists")
            
            # Get batch data from API
            batch_data = self.get_multiple_artists(batch.tolist())
            
            # Process each artist in the batch
            for artist_id in batch:
                if artist_id in batch_data:
                    artist_info = batch_data[artist_id]
                    result = {
                        'artist_id': artist_id,
                        'artist_name': artist_info.get("name", ""),
                        'genres': artist_info.get("genres", []),
                        'popularity': artist_info.get("popularity", 0),
                        'followers': artist_info.get("followers", {}).get("total", 0),
                        'found': True
                    }
                else:
                    result = {
                        'artist_id': artist_id,
                        'artist_name': '',
                        'genres': [],
                        'popularity': 0,
                        'followers': 0,
                        'found': False
                    }
                
                # Cache the result
                self.artist_cache[artist_id] = result
                artist_data[artist_id] = result
            
            # Small delay between batches
            time.sleep(0.1)
        
        # Add genre information to dataframe
        def get_genres_for_id(artist_id):
            if pd.isna(artist_id) or artist_id not in artist_data:
                return ''
            return ', '.join(artist_data[artist_id]['genres'])
        
        def get_artist_name_from_spotify(artist_id):
            if pd.isna(artist_id) or artist_id not in artist_data:
                return ''
            return artist_data[artist_id]['artist_name']
        
        def get_popularity(artist_id):
            if pd.isna(artist_id) or artist_id not in artist_data:
                return 0
            return artist_data[artist_id]['popularity']
        
        def get_followers(artist_id):
            if pd.isna(artist_id) or artist_id not in artist_data:
                return 0
            return artist_data[artist_id]['followers']
        
        # Add new columns
        df['genres'] = df[artist_id_column].apply(get_genres_for_id)
        df['spotify_artist_name'] = df[artist_id_column].apply(get_artist_name_from_spotify)
        df['artist_popularity'] = df[artist_id_column].apply(get_popularity)
        df['artist_followers'] = df[artist_id_column].apply(get_followers)
        
        # Analysis and reporting
        print(f"\n{'='*60}")
        print("GENRE ANALYSIS RESULTS:")
        print(f"{'='*60}")
        
        # Count artists by genre status
        artists_with_genres = sum(1 for data in artist_data.values() if data['genres'])
        artists_without_genres = sum(1 for data in artist_data.values() if data['found'] and not data['genres'])
        artists_not_found = sum(1 for data in artist_data.values() if not data['found'])
        
        
        # Show artists without genres
        if artists_without_genres > 0:
            print(f"\n🎵 Artists found but no genres assigned:")
            for artist_id, data in artist_data.items():
                if data['found'] and not data['genres']:
                    print(f"  • {data['artist_name']} (ID: {artist_id})")
                    print(f"    Popularity: {data['popularity']}, Followers: {data['followers']:,}")
        
        # Show most common genres
        all_genres = []
        for data in artist_data.values():
            all_genres.extend(data['genres'])
        
        if all_genres:
            from collections import Counter
            genre_counts = Counter(all_genres)
            print(f"\n🎶 Top 10 genres in your music:")
            for genre, count in genre_counts.most_common(10):
                print(f"  • {genre}: {count} artists")
        
        # Save updated CSV
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"data/{name}_with_genres{ext}"
        
        df.to_csv(output_file, index=False)
        print(f"\nSaved updated CSV to: {output_file}")
        
        # Save cache
        self.save_cache()
        
        return df

# Example usage
def main():
    # You need to get these from Spotify Developer Dashboard
    # https://developer.spotify.com/dashboard/applications
    CLIENT_ID = 'client_id'
    CLIENT_SECRET = 'client_secret'
    
    # Initialize the fetcher
    fetcher = SpotifyGenreFetcher(CLIENT_ID, CLIENT_SECRET)
    
    # Process your CSV file with artist IDs
    try:
        df = fetcher.process_csv_with_ids("data/StreamingHistory_music.csv")
        print("\nFirst few rows with genres:")
        print(df[['trackname', 'artistname', 'spotify_artist_name', 'genres', 'artist_popularity']].head(10))
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to:")
        print("1. Replace CLIENT_ID and CLIENT_SECRET with your actual Spotify API credentials")
        print("2. Install required packages: pip install pandas requests")
        print("3. Create a Spotify app at https://developer.spotify.com/dashboard/applications")

if __name__ == "__main__":
    main()