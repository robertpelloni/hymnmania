import os
import sys
import logging
import requests
from dotenv import load_dotenv

# Load .env from workspace root or hymn_remaker
load_dotenv("hymn_remaker/.env")
load_dotenv(".env")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hymn_remaker.src.udio_api import UdioAPIClient

logging.basicConfig(level=logging.INFO)
client = UdioAPIClient()

headers = client._get_headers(get_request=True)
print("Using headers Cookie:", headers.get("Cookie", "")[:100], "...")

# Get recent songs to find a valid song ID
print("\nFetching recent songs via /api/songs/me:")
resp = requests.get(f"{client.base_url}/api/songs/me?pageSize=5", headers=headers)
print("Status:", resp.status_code)
recent_ids = []
if resp.status_code == 200:
    data = resp.json()
    songs = data.get("data", [])
    print(f"Found {len(songs)} songs:")
    for song in songs:
        recent_ids.append(song['id'])
        print(f" - ID: {song['id']}, Title: {song.get('title')}, Finished: {song.get('finished')}, Path: {song.get('song_path')}")
else:
    print("Error text:", resp.text[:300])

if recent_ids:
    test_id = recent_ids[0]
    print(f"\n1. Testing /api/songs?songIds={test_id}:")
    resp2 = requests.get(f"{client.base_url}/api/songs?songIds={test_id}", headers=headers)
    print("Status:", resp2.status_code)
    try:
        print("Response keys:", list(resp2.json().keys()))
        print("Response songs type:", type(resp2.json().get("songs")))
        print("Response songs length:", len(resp2.json().get("songs", [])))
        print("First song:", resp2.json().get("songs", [])[:1])
    except Exception as e:
        print("Error parsing response:", e)
        print("Raw text:", resp2.text[:300])

    print(f"\n2. Testing /api/songs/me?songIds={test_id}:")
    resp3 = requests.get(f"{client.base_url}/api/songs/me?songIds={test_id}", headers=headers)
    print("Status:", resp3.status_code)
    try:
        print("Response keys:", list(resp3.json().keys()))
        print("Response data length:", len(resp3.json().get("data", [])))
    except Exception as e:
        print("Error parsing response:", e)
        print("Raw text:", resp3.text[:300])
