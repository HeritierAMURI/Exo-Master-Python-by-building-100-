import os
import requests
from bs4 import BeautifulSoup
from ytmusicapi import YTMusic

# Check for browser.json before doing anything else
if not os.path.exists("browser.json"):
    print("browser.json not found.")
    print("You need to authenticate with YouTube Music first.")
    print("Run one of these commands in your terminal from this project folder:\n")
    print("  Mac:     pbpaste | ytmusicapi browser")
    print("  Windows: ytmusicapi browser\n")
    print("Copy the request headers from Firefox first.")
    print("This will create browser.json.")
    exit()

# Scraping Bakeboard Hot 100
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

url = f"https://appbrewery.github.io/bakeboard-hot-100/{date}"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")
song_names = [tag.getText().strip() for tag in soup.select("h3.chart-entry__title")]

# YouTube Music Authentication
yt = YTMusic("browser.json")

# Create playlist
playlist_name = f"{date} Billboard 100"
playlist_id = yt.create_playlist(
    playlist_name,
    f"Top songs from {date}",
    privacy_status="PRIVATE",
)
print(f"Created playlist: {playlist_name}")

# Search and add each song
for song in song_names:
    try:
        search_results = yt.search(song, filter="songs", limit=1)
        yt.add_playlist_items(playlist_id, [search_results[0]["videoId"]])
        print(f"Added: {song}")
    except Exception as e:
        print(f"Skipped: {song} | Reason: {e}")
