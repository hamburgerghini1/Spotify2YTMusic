import json
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from ytmusicapi import YTMusic
import time

# ==== CONFIGURATION ====
SPOTIFY_CLIENT_ID = 'ADD CLIENT ID'
SPOTIFY_CLIENT_SECRET = 'ADD SECRET'
SPOTIFY_PLAYLIST_IDS = [
    '2vGpb57Gz7NRWHt36hpYbU?si=ee0ccf4ee05046a7',
    '1AqQ7WEqXh2BjIlpz8BfRK?si=d55a7eccffce40d5',
    '13LVS087SqIOGCFpBrQoRj?si=5b3b1a58e030452e',
    '2ifueVAh9zoXqrnMkbPBHF?si=bc3d8e57e5f340bd',
    '02Bs9GDvTGT6KJCToFiwEE?si=a39dafb37025467c',
    '6Hqa9Sn48xKH0RKjGkwh6R?si=bcda3c51d66d4a4e'
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
    print(f"📥 Fetching tracks from Spotify playlist {playlist_id}...")
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    track_list = [{
        'title': item['track']['name'],
        'artist': item['track']['artists'][0]['name']
    } for item in tracks]
    print(f"🎵 Found {len(track_list)} tracks in Spotify playlist.")
    return track_list

# Search and add to YouTube Music playlist
def import_to_ytmusic(tracks, playlist_name):
    print(f"🎯 Creating YouTube Music playlist: {playlist_name}")
    playlist_id = ytmusic.create_playlist(playlist_name, 'Imported from Spotify')
    print(f"✅ Created YTMusic playlist with ID: {playlist_id}")

    video_ids = []
    for i, t in enumerate(tracks, start=1):
        query = f"{t['title']} {t['artist']}"
        print(f"[{i}/{len(tracks)}] 🔍 Searching YTMusic for: {query}")
        search_results = ytmusic.search(query, filter='songs')
        if search_results:
            video_id = search_results[0]['videoId']
            print(f"   🎧 Found match: {search_results[0]['title']} by {search_results[0]['artists'][0]['name']}")
            video_ids.append(video_id)
        else:
            print(f"   ❌ No match found on YouTube Music for: {query}")
        time.sleep(0.5)  # Avoid rate-limiting

    if video_ids:
        print(f"➕ Adding {len(video_ids)} tracks to the YouTube Music playlist...")
        ytmusic.add_playlist_items(playlist_id, video_ids)
        print(f"✅ Successfully added {len(video_ids)} tracks to '{playlist_name}'")
    else:
        print("⚠️ No songs could be added (no matches found).")

# Main process
for playlist_url in SPOTIFY_PLAYLIST_IDS:
    playlist_id = playlist_url.split("?")[0]
    print(f"\n=== 🚀 Processing Spotify Playlist: {playlist_id} ===")
    try:
        playlist_info = sp.playlist(playlist_id)
        playlist_name = PLAYLIST_NAME_PREFIX + playlist_info['name']
        tracks = fetch_spotify_tracks(playlist_id)
        import_to_ytmusic(tracks, playlist_name)
    except Exception as e:
        print(f"❌ Failed to import {playlist_id}: {e}")
