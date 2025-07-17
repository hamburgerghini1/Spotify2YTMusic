## Spotify To Youtube Music importer - also vice versa

Linux script of Spo2Ytm is tested, but windows version and both Ytm2Spo scripts are not.

Made with ChatGPT, I'm not liable for errors etc

1. Install dependencies
   On Arch
   ```bash
   yay -S python-spotipy python-ytmusicapi
   ```
   Or use pipx.
   
3. Get your Youtube Music token [here](https://ytmusicapi.readthedocs.io/en/stable/usage.html#authenticated) (Firefox is recommended and is much easier)
   Go to youtube music on firefox, press Ctrl-Shift-I and go to network tab and filter by /browse, click to your library or home page until you see the 
   token
5. Create Spotify Dev application at [Spotify for Developers](https://developer.spotify.com) (I named it Spo2YTM)
6. Edit the script and add your client id and the secret
7. Copy playlist link from Spotify (remove the start of the link, leave only the part after last / )
   Remove the ones I left there for reference
8. Script should work as expected

Made this since I didn't want to pay for Soundiiz lol
