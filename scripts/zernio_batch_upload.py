#!/usr/bin/env python3
"""Zernio Batch TikTok Uploader - Compress and upload videos via Zernio API"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Load API key
ZERNIO_API_KEY = ""
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.startswith("ZERNIO_API_KEY="):
            ZERNIO_API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

HEADERS_JSON = {
    "Authorization": f"Bearer {ZERNIO_API_KEY}",
    "Content-Type": "application/json",
}
HEADERS_AUTH = {"Authorization": f"Bearer {ZERNIO_API_KEY}"}
PROFILE_ID = "6a73c427ff8fcb524a407cc6"
TIKTOK_ACCOUNT_ID = "6a73eb85d0fe733d1a888051"
ZERNIO_MEDIA_LIMIT = 4 * 1024 * 1024  # 4MB

VERT_DIR = Path(__file__).parent.parent / "generated" / "vertical"
COMPRESSED_DIR = Path(__file__).parent.parent / "generated" / "vertical_compressed"
COMPRESSED_DIR.mkdir(exist_ok=True)

POSTED_LOG = Path(__file__).parent.parent / ".zernio_posted.json"


def load_posted():
    if POSTED_LOG.exists():
        return json.loads(POSTED_LOG.read_text())
    return {}


def save_posted(posted):
    POSTED_LOG.write_text(json.dumps(posted, indent=2))


def get_duration(video_path):
    r = subprocess.run(
        ["ffmpeg", "-i", str(video_path)], capture_output=True, text=True, timeout=30
    )
    for line in r.stderr.split("\n"):
        if "Duration" in line:
            d = line.split("Duration:")[1].split(",")[0].strip()
            parts = d.split(":")
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return 60  # default


def compress_video(video_path, out_path, target_mb=3.5):
    duration = get_duration(video_path)
    target_bytes = target_mb * 1024 * 1024

    # TikTok requires min 720p, so keep 1080x1920 but with very low bitrate
    for attempt in range(5):
        total_br = int((target_bytes * 8 * 0.6) / duration)  # 60% of theoretical
        video_br = max(30000, total_br - 48000)

        r = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-vf",
                "scale=720:1280",
                "-b:v",
                f"{video_br}",
                "-maxrate",
                f"{video_br}",
                "-bufsize",
                f"{video_br}",
                "-b:a",
                "48k",
                "-movflags",
                "+faststart",
                str(out_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if os.path.exists(out_path) and os.path.getsize(out_path) <= target_bytes:
            return True
        if os.path.exists(out_path):
            os.remove(out_path)

    return False


def upload_to_zernio(video_path):
    with open(video_path, "rb") as f:
        r = requests.post(
            "https://zernio.com/api/v1/media",
            headers=HEADERS_AUTH,
            files={"files": (os.path.basename(video_path), f, "video/mp4")},
            timeout=300,
        )
    if r.status_code == 200:
        return r.json().get("files", [{}])[0].get("url")
    return None


def create_post(media_url, caption):
    schedule_time = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
    post_data = {
        "profileId": PROFILE_ID,
        "platform": "tiktok",
        "platforms": [{"platform": "tiktok", "accountId": TIKTOK_ACCOUNT_ID}],
        "content": caption,
        "mediaItems": [{"type": "video", "url": media_url}],
        "scheduledFor": schedule_time,
        "status": "scheduled",
    }
    r = requests.post(
        "https://zernio.com/api/v1/posts",
        headers=HEADERS_JSON,
        json=post_data,
        timeout=30,
    )
    if r.status_code == 201:
        return r.json().get("post", {})
    return None


def wait_for_publish(post_id, max_wait=300):
    for i in range(max_wait // 15):
        time.sleep(15)
        r = requests.get(
            f"https://zernio.com/api/v1/posts/{post_id}",
            headers=HEADERS_JSON,
            timeout=30,
        )
        data = r.json()
        post = data.get("post", data)
        status = post.get("status")
        plat = post.get("platforms", [{}])[0]
        ps = plat.get("status", "")
        ext = plat.get("externalPostId", "")
        err = plat.get("errorMessage", "")

        if status == "published" or ps == "published":
            return True, ext
        if status == "failed" or ps in ["failed", "error"]:
            return False, err
    return False, "timeout"


def build_caption(filename):
    title = (
        filename.replace("_vertical.mp4", "")
        .replace(".mp4", "")
        .replace(" - ", ": ", 1)
    )
    return f"{title}\n\n#ResurrectingBeats #Hymnmania #ChristianPsytrance #Psytrance #ElectronicMusic #WorshipMusic #HymnRemix #ElectronicWorship #2026"


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    posted = load_posted()

    videos = sorted([f for f in os.listdir(VERT_DIR) if f.endswith("_vertical.mp4")])
    unposted = [v for v in videos if v not in posted]

    print(f"Total: {len(videos)} | Posted: {len(posted)} | Remaining: {len(unposted)}")
    print(f"Uploading: {min(limit, len(unposted))} videos\n")

    success = 0
    failed = 0

    for i, video in enumerate(unposted[:limit]):
        video_path = VERT_DIR / video
        compressed_path = COMPRESSED_DIR / video.replace(".mp4", "_c.mp4")

        print(f"[{i + 1}/{min(limit, len(unposted))}] {video[:60]}")

        # Compress
        if not compressed_path.exists():
            print("  Compressing...", end=" ", flush=True)
            if compress_video(video_path, compressed_path):
                size = os.path.getsize(compressed_path) / (1024 * 1024)
                print(f"{size:.1f}MB")
            else:
                print("FAILED")
                failed += 1
                continue
        else:
            print(
                f"  Already compressed: {os.path.getsize(compressed_path) / (1024 * 1024):.1f}MB"
            )

        # Upload to Zernio
        print("  Uploading to Zernio...", end=" ", flush=True)
        media_url = upload_to_zernio(compressed_path)
        if not media_url:
            print("FAILED")
            failed += 1
            continue
        print("OK")

        # Create post
        caption = build_caption(video)
        print("  Creating post...", end=" ", flush=True)
        post = create_post(media_url, caption)
        if not post:
            print("FAILED")
            failed += 1
            continue

        post_id = post.get("_id")
        print(f"ID={post_id[:12]}")

        # Wait for publish
        print("  Publishing...", end=" ", flush=True)
        ok, result = wait_for_publish(post_id)
        if ok:
            print(f"PUBLISHED! ext={result[:20] if result else ''}")
            posted[video] = {
                "post_id": post_id,
                "external_id": result,
                "time": datetime.now().isoformat(),
            }
            save_posted(posted)
            success += 1
        else:
            print(f"FAILED: {result[:60]}")
            failed += 1

        # Rate limit
        time.sleep(5)

    print(f"\n{'=' * 50}")
    print(f"Results: {success} published, {failed} failed")
    print(f"Total posted: {len(posted)}/{len(videos)}")


if __name__ == "__main__":
    main()
