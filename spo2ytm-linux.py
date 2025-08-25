import json
import sys
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from ytmusicapi import YTMusic
import time
import os

# ==== CONFIGURATION ====
SPOTIFY_CLIENT_ID = 'add id'
SPOTIFY_CLIENT_SECRET = 'add secret'
YTM_HEADERS_FILE = 'headers_auth.json'
PLAYLIST_NAME_PREFIX = 'Imported: '
# ========================

def extract_playlist_id(playlist_url):
    """Extract the playlist ID from a Spotify playlist URL"""
    if 'spotify.com/playlist/' in playlist_url:
        playlist_id = playlist_url.split('playlist/')[-1].split('?')[0]
        return playlist_id
    return None

def print_usage():
    print("Usage: python spo2ytm-linux.py <spotify_playlist_url> [spotify_playlist_url2 ...]")
    print("Example: python spo2ytm-linux.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
    sys.exit(1)

# Authenticate Spotify
print("🔐 Authenticating with Spotify...")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))
print("✅ Spotify authentication successful.")

# Authenticate YouTube Music
print("🔐 Authenticating with YouTube Music...")
try:
    if not os.path.exists(YTM_HEADERS_FILE):
        print(f"❌ {YTM_HEADERS_FILE} not found!")
        print("\nTo setup authentication:")
        print("1. Run: python -m ytmusicapi oauth")
        print("2. Follow the prompts to complete authentication")
        sys.exit(1)
    
    try:
        with open(YTM_HEADERS_FILE, 'r') as f:
            headers_content = f.read().strip()
            if not headers_content:
                raise ValueError("Headers file is empty")
    except Exception as e:
        print(f"❌ Error reading {YTM_HEADERS_FILE}: {str(e)}")
        print("The file exists but may be corrupted.")
        print("\nPlease recreate the authentication file:")
        print("1. Delete the existing headers_auth.json file:")
        print(f"   rm {YTM_HEADERS_FILE}")
        print("2. Run: python -m ytmusicapi oauth")
        print("3. Follow the prompts to generate new credentials")
        sys.exit(1)
        
    ytmusic = YTMusic(YTM_HEADERS_FILE)
    # Verify authentication works
    try:
        ytmusic.get_library_playlists(limit=1)
        print("✅ YouTube Music authentication successful.")
    except Exception as auth_error:
        print("❌ Authentication test failed!")
        print(f"Error: {str(auth_error)}")
        print("\nYour credentials appear to be invalid. Please recreate them:")
        print(f"1. rm {YTM_HEADERS_FILE}")
        print("2. Go to https://music.youtube.com and ensure you're logged in")
        print("3. Run: python -m ytmusicapi oauth")
        print("4. Follow the prompts carefully to generate new credentials")
        sys.exit(1)
        
except Exception as e:
    print("❌ YouTube Music authentication failed!")
    print(f"Error: {str(e)}")
    print("\nUnexpected error. Please try these steps:")
    print(f"1. rm {YTM_HEADERS_FILE}")
    print("2. Run: python -m ytmusicapi oauth")
    print("3. Follow the prompts to generate new credentials")
    sys.exit(1)

# Fetch playlist tracks from Spotify
def fetch_spotify_tracks(playlist_id):
    print("📥 Fetching tracks from Spotify...")
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    track_data = []
    for item in tracks:
        name = item['track']['name']
        artist = item['track']['artists'][0]['name']
        print(f"🎵 Found: {name} - {artist}")
        track_data.append({'title': name, 'artist': artist})
    return track_data

# Search and add to YouTube Music playlist
def import_to_ytmusic(tracks, playlist_name):
    global ytmusic  # Move global declaration to top of function
    print(f"\n📀 Creating YT Music playlist: {playlist_name}")
    
    # Try to create playlist with retry
    max_retries = 3
    for attempt in range(max_retries):
        try:
            playlist_id = ytmusic.create_playlist(playlist_name, 'Imported from Spotify')
            print(f"✅ Created playlist with ID: {playlist_id}")
            break
        except Exception as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                print("❌ Authentication error detected")
                if attempt < max_retries - 1:
                    print(f"Attempting to refresh authentication (attempt {attempt + 1}/{max_retries})...")
                    # Re-initialize YTMusic
                    ytmusic = YTMusic(YTM_HEADERS_FILE)
                    continue
                else:
                    print("\n⚠️ Authentication failed after retries. Please:")
                    print("1. Delete your current headers_auth.json")
                    print("2. Go to https://music.youtube.com and ensure you're logged in")
                    print("3. Run: python -m ytmusicapi oauth")
                    print("4. Try running the script again")
                    raise
            else:
                print(f"❌ Failed to create playlist: {e}")
                raise
    
    success_count = 0
    for t in tracks:
        query = f"{t['title']} {t['artist']}"
        print(f"🔍 Searching: {query}")
        try:
            search_results = ytmusic.search(query, filter='songs')
            if search_results:
                video_id = search_results[0]['videoId']
                print(f"🎧 Match: https://music.youtube.com/watch?v={video_id}")
                try:
                    ytmusic.add_playlist_items(playlist_id, [video_id])
                    success_count += 1
                    print(f"   ✅ Added: {t['title']} by {t['artist']}")
                except Exception as e:
                    if "401" in str(e):
                        print("❌ Authentication error. Please re-run the script.")
                        raise
                    print(f"   ❌ Failed to add {video_id}: {e}")
            else:
                print(f"   ❌ Not found: {query}")
        except Exception as e:
            print(f"   ❌ Error processing {query}: {e}")
        time.sleep(1)  # Increased delay between requests
    
    print(f"\n✅ Import complete! Successfully added {success_count} of {len(tracks)} tracks")

# Main process
for playlist_url in sys.argv[1:]:
    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        print(f"❌ Invalid Spotify playlist URL: {playlist_url}")
        continue

    print(f"\n--- Processing playlist: {playlist_id} ---")
    try:
        playlist_info = sp.playlist(playlist_id)
        playlist_name = PLAYLIST_NAME_PREFIX + playlist_info['name']
        tracks = fetch_spotify_tracks(playlist_id)
        import_to_ytmusic(tracks, playlist_name)
    except Exception as e:
        print(f"❌ Failed to import {playlist_id}: {e}")
