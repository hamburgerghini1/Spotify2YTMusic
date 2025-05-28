1. Install dependencies
   On Arch
   ```bash
   yay -S python-spotipy python-ytmusicapi
   ```
   Or use pipx.
   
3. Get your Youtube Music token [here](https://ytmusicapi.readthedocs.io/en/stable/usage.html#authenticated) (Firefox is recommended and is much easier)
4. Create Spotify Dev application at [Spotify for Developers](https://developer.spotify.com) (I named it Spo2YTM)
5. Edit the script and add your client id and the secret
6. Copy playlist link from Spotify (remove the start of the link, leave only the part after last / )
7. Script should work as expected
