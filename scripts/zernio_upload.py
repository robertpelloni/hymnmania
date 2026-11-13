#!/usr/bin/env python3
"""
Zernio Integration for HymnMania
Upload videos to TikTok, YouTube, and other platforms via Zernio API
API: https://zernio.com/api/v1
"""

import os
import requests
import argparse
import time
from pathlib import Path

# Zernio API configuration
ZERNIO_BASE_URL = "https://zernio.com/api/v1"
ZERNIO_API_KEY = os.environ.get("ZERNIO_API_KEY", "")

# Load from .env if exists
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("ZERNIO_API_KEY="):
            ZERNIO_API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

HEADERS = {
    "Authorization": f"Bearer {ZERNIO_API_KEY}",
    "Content-Type": "application/json",
}

TIMEOUT = 30  # seconds


def check_api_key():
    """Check if API key is configured"""
    if not ZERNIO_API_KEY:
        print("ERROR: ZERNIO_API_KEY not set!")
        print("\nTo set up Zernio:")
        print("1. Go to https://zernio.com and sign up (free, no credit card)")
        print("2. Go to Settings → API Keys")
        print("3. Click 'Create API Key'")
        print("4. Copy the key (sk_...)")
        print("5. Set it in .env file:")
        print('   ZERNIO_API_KEY="sk_..."')
        print("\nOr set as environment variable:")
        print('   export ZERNIO_API_KEY="sk_..."')
        return False
    return True


def create_profile(
    name="HymnMania", description="Resurrecting Beats - Electronic Worship Music"
):
    """Create a Zernio profile for organizing accounts"""
    try:
        response = requests.post(
            f"{ZERNIO_BASE_URL}/profiles",
            headers=HEADERS,
            json={"name": name, "description": description},
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Profile created: {data.get('_id')}")
            return data
        else:
            print(f"Error creating profile: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def get_profiles():
    """List all profiles"""
    try:
        response = requests.get(
            f"{ZERNIO_BASE_URL}/profiles", headers=HEADERS, timeout=TIMEOUT
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting profiles: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []


def get_connect_url(platform, profile_id):
    """Get OAuth URL for connecting a social media account"""
    try:
        response = requests.get(
            f"{ZERNIO_BASE_URL}/connect/{platform}",
            headers=HEADERS,
            params={"profileId": profile_id},
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("authUrl")
        else:
            print(f"Error getting connect URL: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def upload_video_to_tiktok(video_path, caption, profile_id=None):
    """Upload a video to TikTok via Zernio"""
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        return None

    # Get profile ID if not provided
    if not profile_id:
        profiles = get_profiles()
        if not profiles:
            print("No profiles found. Create one first.")
            return None
        profile_id = profiles[0].get("_id")

    # First, upload the video file
    print(f"Uploading video: {os.path.basename(video_path)}")

    try:
        with open(video_path, "rb") as f:
            upload_response = requests.post(
                f"{ZERNIO_BASE_URL}/media/upload",
                headers={"Authorization": f"Bearer {ZERNIO_API_KEY}"},
                files={"file": (os.path.basename(video_path), f, "video/mp4")},
                timeout=300,  # Longer timeout for video uploads
            )

        if upload_response.status_code != 200:
            print(f"Upload failed: {upload_response.status_code}")
            print(upload_response.text)
            return None

        media_data = upload_response.json()
        media_id = media_data.get("_id") or media_data.get("mediaId")
        print(f"Media uploaded: {media_id}")
    except requests.exceptions.RequestException as e:
        print(f"Upload request failed: {e}")
        return None
    except OSError as e:
        print(f"File error: {e}")
        return None

    # Create the post
    post_data = {
        "profileId": profile_id,
        "platform": "tiktok",
        "mediaId": media_id,
        "caption": caption,
        "settings": {
            "privacy": "public",
            "isAigc": True,  # AI-generated content flag
        },
    }

    try:
        post_response = requests.post(
            f"{ZERNIO_BASE_URL}/posts", headers=HEADERS, json=post_data, timeout=TIMEOUT
        )

        if post_response.status_code == 200:
            post_data = post_response.json()
            print(f"Post created: {post_data.get('_id')}")
            return post_data
        else:
            print(f"Post failed: {post_response.status_code}")
            print(post_response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Post request failed: {e}")
        return None


def batch_upload_tiktok(video_dir, limit=5):
    """Batch upload vertical videos to TikTok"""
    video_dir = Path(video_dir)
    if not video_dir.exists():
        print(f"Directory not found: {video_dir}")
        return

    # Get vertical videos
    videos = sorted(video_dir.glob("*_vertical.mp4"))
    if not videos:
        print("No vertical videos found")
        return

    print(f"Found {len(videos)} vertical videos")

    # Upload first N videos
    uploaded = 0
    for video in videos[:limit]:
        # Build caption from filename
        title = video.stem.replace("_vertical", "").replace(" - ", ": ", 1)
        caption = f"""{title}

#ResurrectingBeats #Hymnmania #ElectronicMusic #ChristianMusic #Worship #Remix #AIMusic #HymnRemix #ElectronicWorship #2026"""

        print(f"\n{'=' * 60}")
        print(f"Uploading: {video.name}")
        print(f"Caption: {caption[:80]}...")

        result = upload_video_to_tiktok(str(video), caption)
        if result:
            uploaded += 1
            print(f"✓ Success ({uploaded}/{limit})")
        else:
            print("✗ Failed")

        # Rate limiting - wait between uploads
        if uploaded < limit:
            time.sleep(5)

    print(f"\n{'=' * 60}")
    print(f"Uploaded: {uploaded}/{limit}")


def main():
    parser = argparse.ArgumentParser(description="Zernio Integration for HymnMania")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up Zernio integration")

    # Profiles command
    profiles_parser = subparsers.add_parser("profiles", help="Manage profiles")
    profiles_parser.add_argument(
        "--create", action="store_true", help="Create new profile"
    )
    profiles_parser.add_argument("--list", action="store_true", help="List profiles")

    # Connect command
    connect_parser = subparsers.add_parser(
        "connect", help="Connect social media account"
    )
    connect_parser.add_argument(
        "--platform",
        required=True,
        choices=["tiktok", "youtube", "instagram", "facebook", "twitter"],
    )
    connect_parser.add_argument("--profile-id", help="Profile ID")

    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload video to platform")
    upload_parser.add_argument("--video", required=True, help="Video file path")
    upload_parser.add_argument("--caption", required=True, help="Post caption")
    upload_parser.add_argument(
        "--platform", default="tiktok", choices=["tiktok", "youtube", "instagram"]
    )
    upload_parser.add_argument("--profile-id", help="Profile ID")

    # Batch upload command
    batch_parser = subparsers.add_parser("batch", help="Batch upload videos")
    batch_parser.add_argument(
        "--dir", default="generated/vertical", help="Video directory"
    )
    batch_parser.add_argument(
        "--limit", type=int, default=5, help="Number of videos to upload"
    )
    batch_parser.add_argument(
        "--platform", default="tiktok", choices=["tiktok", "youtube", "instagram"]
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Check API key for all commands except setup
    if args.command != "setup" and not check_api_key():
        return

    if args.command == "setup":
        print("Zernio Integration Setup")
        print("=" * 60)
        print("\n1. Go to https://zernio.com and sign up (free)")
        print("2. Go to Settings → API Keys")
        print("3. Click 'Create API Key'")
        print("4. Copy the key (sk_...)")
        print("\n5. Add to .env file:")
        print('   ZERNIO_API_KEY="sk_..."')
        print("\n6. Run this script to connect your TikTok account:")
        print("   python zernio_upload.py connect --platform tiktok")

    elif args.command == "profiles":
        if args.create:
            create_profile()
        elif args.list:
            profiles = get_profiles()
            if profiles:
                print("Profiles:")
                for p in profiles:
                    print(f"  {p.get('_id')}: {p.get('name')}")
            else:
                print("No profiles found")

    elif args.command == "connect":
        url = get_connect_url(args.platform, args.profile_id)
        if url:
            print(f"Open this URL to connect your {args.platform} account:")
            print(url)

    elif args.command == "upload":
        result = upload_video_to_tiktok(args.video, args.caption, args.profile_id)
        if result:
            print("Upload successful!")

    elif args.command == "batch":
        if args.platform == "tiktok":
            batch_upload_tiktok(args.dir, args.limit)
        else:
            print(f"Batch upload for {args.platform} not implemented yet")


if __name__ == "__main__":
    main()
