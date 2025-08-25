import sys
import json
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from ytmusicapi import YTMusic
import time

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
ytmusic = YTMusic(YTM_HEADERS_FILE)
print("✅ YouTube Music authentication successful.")

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
    print(f"\n📀 Creating YT Music playlist: {playlist_name}")
    playlist_id = ytmusic.create_playlist(playlist_name, 'Imported from Spotify')
    print(f"✅ Created playlist with ID: {playlist_id}")

    for t in tracks:
        query = f"{t['title']} {t['artist']}"
        print(f"🔍 Searching: {query}")
        search_results = ytmusic.search(query, filter='songs')
        if search_results:
            video_id = search_results[0]['videoId']
            print(f"🎧 Match: https://music.youtube.com/watch?v={video_id}")
            try:
                ytmusic.add_playlist_items(playlist_id, [video_id])
                print(f"   ✅ Added: {t['title']} by {t['artist']}")
            except Exception as e:
                print(f"   ❌ Failed to add {video_id}: {e}")
        else:
            print(f"   ❌ Not found: {query}")
        time.sleep(0.5)

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
