import os
import sys
import time
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv
from datetime import datetime

# ==== CONFIGURATION ====
YTM_HEADERS_FILE = 'headers_auth.json'
YTM_PLAYLIST_ID = 'YOUR_YTM_PLAYLIST_ID'
SPOTIFY_CLIENT_ID = 'add id'
SPOTIFY_CLIENT_SECRET = 'add secret'
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'
SPOTIFY_SCOPE = 'playlist-modify-public playlist-modify-private'
PLAYLIST_NAME_PREFIX = 'Imported from YTMusic: '
# =======================

def windows_clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def windows_pause():
    if os.name == 'nt':
        os.system('pause')
    else:
        input('Press Enter to continue...')

def check_headers_file():
    if not os.path.exists(YTM_HEADERS_FILE):
        print(f"❌ YouTube Music headers file '{YTM_HEADERS_FILE}' not found.")
        print("Please export your YouTube Music cookies using the instructions at:")
        print("https://ytmusicapi.readthedocs.io/en/stable/setup.html#authenticated-requests")
        windows_pause()
        sys.exit(1)

def main():
    windows_clear()
    print("==== YT Music to Spotify Playlist Importer (Windows) ====")
    check_headers_file()
    ytmusic = YTMusic(YTM_HEADERS_FILE)

    # Authenticate Spotify
    print("\n🔐 Authenticating with Spotify...")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    ))
    print("✅ Spotify authentication successful.")

    # Get playlist info and tracks from YT Music
    print(f"\n📥 Fetching YT Music playlist: {YTM_PLAYLIST_ID}")
    playlist = ytmusic.get_playlist(YTM_PLAYLIST_ID, limit=1000)
    playlist_name = PLAYLIST_NAME_PREFIX + playlist['title']
    tracks = [{'title': t['title'], 'artist': t['artists'][0]['name']} for t in playlist['tracks']]

    print(f"Found {len(tracks)} tracks in YT Music playlist '{playlist['title']}'.")

    # Create Spotify playlist
    user_id = sp.me()['id']
    sp_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False, description='Imported from YouTube Music')
    sp_playlist_id = sp_playlist['id']
    print(f"✅ Created Spotify playlist: {playlist_name}")

    missing_tracks = []
    success_count = 0

    for t in tracks:
        query = f"{t['title']} {t['artist']}"
        print(f"🔍 Searching Spotify: {query}")
        try:
            results = sp.search(q=query, type='track', limit=1)
            items = results['tracks']['items']
            if items:
                track_id = items[0]['id']
                sp.playlist_add_items(sp_playlist_id, [track_id])
                success_count += 1
                print(f"   ✅ Added: {t['title']} by {t['artist']}")
            else:
                print(f"   ❌ Not found on Spotify: {t['title']} by {t['artist']}")
                missing_tracks.append({
                    'title': t['title'], 
                    'artist': t['artist'],
                    'reason': 'Not found on Spotify'
                })
        except Exception as e:
            print(f"   ❌ Error processing {query}: {e}")
            missing_tracks.append({
                'title': t['title'], 
                'artist': t['artist'],
                'reason': f'Error: {str(e)}'
            })
        time.sleep(0.5)

    # Create CSV file for missing tracks
    if missing_tracks:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f'missing_tracks_ytm2spo_{timestamp}.csv'
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['title', 'artist', 'reason'])
                writer.writeheader()
                writer.writerows(missing_tracks)
            print(f"\n📝 Created CSV file with {len(missing_tracks)} missing tracks: {csv_filename}")
        except Exception as e:
            print(f"❌ Failed to create CSV file: {e}")

    print(f"\n✅ Import complete! Successfully added {success_count} of {len(tracks)} tracks")
    windows_pause()

if __name__ == "__main__":
    main()