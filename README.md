## Spotify To Youtube Music importer

The script is for Linux, but I don't see why it wouldn't work on macOS or Windows too

1. Install dependencies
   On Arch
   ```bash
   yay -S python-spotipy python-ytmusicapi
   ```
   Or use pipx.
   
3. Get your Youtube Music token [here](https://ytmusicapi.readthedocs.io/en/stable/usage.html#authenticated) (Firefox is recommended and is much easier)
   Go to youtube music on firefox, press Ctrl-Shift-I and go to network tab and filter by /browse, click to your library to home page until you see the 
   token
5. Create Spotify Dev application at [Spotify for Developers](https://developer.spotify.com) (I named it Spo2YTM)
6. Edit the script and add your client id and the secret
7. Copy playlist link from Spotify (remove the start of the link, leave only the part after last / )
   Remove the ones I left there for reference
8. Script should work as expected

Made this since I didn't want to pay for Soundiiz lol
