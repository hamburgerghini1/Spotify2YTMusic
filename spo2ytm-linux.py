import json
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from ytmusicapi import YTMusic
import time

# ==== CONFIGURATION ====
SPOTIFY_CLIENT_ID = 'add id'
SPOTIFY_CLIENT_SECRET = 'add secret'
SPOTIFY_PLAYLIST_IDS = [
    '2vGpb57Gz7NRWHt36hpYbU?si=ee0ccf4ee05046a7',
    '13LVS087SqIOGCFpBrQoRj?si=5b3b1a58e030452e',
    '2ifueVAh9zoXqrnMkbPBHF?si=bc3d8e57e5f340bd',
    '02Bs9GDvTGT6KJCToFiwEE?si=a39dafb37025467c',
    '6Hqa9Sn48xKH0RKjGkwh6R?si=bcda3c51d66d4a4e',
    '176aQaRwOaxlp7HPirgE6E?si=f63726034c2c490e',
]
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

# Main process
for playlist_url in SPOTIFY_PLAYLIST_IDS:
    playlist_id = playlist_url.split("?")[0]

    print(f"\n--- Processing playlist: {playlist_id} ---")
    try:
        playlist_info = sp.playlist(playlist_id)
        playlist_name = PLAYLIST_NAME_PREFIX + playlist_info['name']
        tracks = fetch_spotify_tracks(playlist_id)
        import_to_ytmusic(tracks, playlist_name)
    except Exception as e:
        print(f"❌ Failed to import {playlist_id}: {e}")
