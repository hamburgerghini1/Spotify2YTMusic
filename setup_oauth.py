from ytmusicapi import setup

def setup_ytmusic():
    print("Setting up YouTube Music authentication...")
    print("\nPlease follow these steps:")
    print("1. Open https://music.youtube.com in your browser")
    print("2. Make sure you're logged in")
    print("3. Press F12 to open Developer Tools")
    print("4. Go to Network tab")
    print("5. Refresh the page")
    print("6. Click on any request to music.youtube.com")
    print("7. In the Headers tab, scroll to 'Request Headers'")
    print("8. Copy everything under Request Headers")
    print("\nWhen ready, press Enter to continue...")
    input()

    try:
        setup(filepath='headers_auth.json')
        print("\n✅ Authentication file created successfully!")
        print("You can now run your playlist import script.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please try again and make sure to copy the full request headers.")

if __name__ == "__main__":
    setup_ytmusic()
