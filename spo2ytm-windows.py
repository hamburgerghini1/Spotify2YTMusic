import sys
import json
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from ytmusicapi import YTMusic
import time
import os
import csv
from datetime import datetime

# ==== CONFIGURATION ====
SPOTIFY_CLIENT_ID = 'add id'
SPOTIFY_CLIENT_SECRET = 'add secret'
YTM_HEADERS_FILE = 'headers_auth.json'
PLAYLIST_NAME_PREFIX = 'Imported: '
# ========================

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
        print("1. Delete the existing headers_auth.json file")
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
        print("1. Delete your current headers_auth.json")
        print("2. Go to https://music.youtube.com and ensure you're logged in")
        print("3. Run: python -m ytmusicapi oauth")
        print("4. Follow the prompts carefully to generate new credentials")
        sys.exit(1)
        
except Exception as e:
    print("❌ YouTube Music authentication failed!")
    print(f"Error: {str(e)}")
    print("\nUnexpected error. Please try these steps:")
    print("1. Delete headers_auth.json")
    print("2. Run: python -m ytmusicapi oauth")
    print("3. Follow the prompts to generate new credentials")
    sys.exit(1)

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

def import_to_ytmusic(tracks, playlist_name):
    global ytmusic
    print(f"\n📀 Creating YT Music playlist: {playlist_name}")
    
    missing_tracks = []
    
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
                    missing_tracks.append({'title': t['title'], 'artist': t['artist'], 'reason': f'Failed to add: {str(e)}'})
            else:
                print(f"   ❌ Not found: {query}")
                missing_tracks.append({'title': t['title'], 'artist': t['artist'], 'reason': 'Not found in YouTube Music'})
        except Exception as e:
            print(f"   ❌ Error processing {query}: {e}")
            missing_tracks.append({'title': t['title'], 'artist': t['artist'], 'reason': f'Error: {str(e)}'})
        time.sleep(1)

    # Create CSV file for missing tracks
    if missing_tracks:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f'missing_tracks_{timestamp}.csv'
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['title', 'artist', 'reason'])
                writer.writeheader()
                writer.writerows(missing_tracks)
            print(f"\n📝 Created CSV file with {len(missing_tracks)} missing tracks: {csv_filename}")
        except Exception as e:
            print(f"❌ Failed to create CSV file: {e}")
    
    print(f"\n✅ Import complete! Successfully added {success_count} of {len(tracks)} tracks")

# === Main process ===
if len(sys.argv) > 1:
    playlist_urls = sys.argv[1:]
else:
    playlist_urls = input("📋 Paste Spotify playlist URLs (comma separated): ").split(",")

for playlist_url in playlist_urls:
    playlist_id = playlist_url.strip().split("/")[-1].split("?")[0]  # extract ID from link

    print(f"\n--- Processing playlist: {playlist_id} ---")
    try:
        playlist_info = sp.playlist(playlist_id)
        playlist_name = PLAYLIST_NAME_PREFIX + playlist_info['name']
        tracks = fetch_spotify_tracks(playlist_id)
        import_to_ytmusic(tracks, playlist_name)
    except Exception as e:
        print(f"❌ Failed to import {playlist_id}: {e}")
