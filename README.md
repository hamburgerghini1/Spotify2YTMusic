## Spotify To Youtube Music importer - also vice versa

Linux script of Spo2Ytm is tested, but windows version and both Ytm2Spo scripts are not.

Made with ChatGPT, I'm not liable for errors etc

1. Install dependencies
   On Arch
   ```bash
   yay -S python-spotipy python-ytmusicapi
   ```
   Or use pipx.
   
2. Run setup_oauth.py to get YT Music headers, use firefox.
3. Run the script with and add playlists link to the end, for multiple playlists use quotes
