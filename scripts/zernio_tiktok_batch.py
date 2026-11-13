#!/usr/bin/env python3
"""
Zernio TikTok Batch Uploader
Pipeline: Upload to Catbox.moe -> Create Zernio post -> Publish to TikTok
"""

import os
import sys
import json
import time
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
PROFILE_ID = "6a73c427ff8fcb524a407cc6"
TIKTOK_ACCOUNT_ID = "6a73eb85d0fe733d1a888051"

VERT_DIR = Path(__file__).parent.parent / "generated" / "vertical"
POSTED_LOG = Path(__file__).parent.parent / ".zernio_posted.json"
CATBOX_MAX_MB = 190  # Catbox limit is 200MB, leave margin
POST_DELAY = 180  # 3 minutes between posts


def load_posted():
    if POSTED_LOG.exists():
        return json.loads(POSTED_LOG.read_text())
    return {}


def save_posted(posted):
    POSTED_LOG.write_text(json.dumps(posted, indent=2))


def safe_filename(name):
    return (
        name.replace("[A]", "A")
        .replace("[B]", "B")
        .replace("[Magnific]", "Magnific")
        .replace(" ", "_")
    )


def upload_to_catbox(video_path, safe_name):
    """Upload video to Catbox.moe and return direct URL"""
    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    if size_mb > CATBOX_MAX_MB:
        print(f"  SKIP: {size_mb:.0f}MB > {CATBOX_MAX_MB}MB limit")
        return None

    try:
        with open(video_path, "rb") as f:
            r = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": (safe_name, f, "video/mp4")},
                timeout=900,
            )
        if r.status_code == 200 and r.text.strip().startswith("http"):
            return r.text.strip()
        else:
            print(f"  Upload error: {r.status_code} {r.text[:80]}")
            return None
    except Exception as e:
        print(f"  Upload exception: {str(e)[:80]}")
        return None


def create_tiktok_post(video_url, caption):
    """Create a Zernio post scheduled for immediate publish"""
    schedule_time = (
        (datetime.now(timezone.utc) + timedelta(minutes=2))
        .replace(second=0, microsecond=0)
        .isoformat()
    )

    post_data = {
        "profileId": PROFILE_ID,
        "platform": "tiktok",
        "platforms": [{"platform": "tiktok", "accountId": TIKTOK_ACCOUNT_ID}],
        "content": caption,
        "mediaItems": [{"type": "video", "url": video_url}],
        "scheduledFor": schedule_time,
        "status": "scheduled",
    }

    try:
        r = requests.post(
            "https://zernio.com/api/v1/posts",
            headers=HEADERS_JSON,
            json=post_data,
            timeout=30,
        )
        if r.status_code == 201:
            return r.json().get("post", {})
        elif r.status_code == 409:
            print("(duplicate)")
        elif r.status_code == 429:
            print("(rate limited)")
            time.sleep(300)  # Wait 5 min on rate limit
        else:
            print(f"(HTTP {r.status_code})")
    except Exception as e:
        print(f"(error: {str(e)[:40]})")
    return None


def wait_for_publish(post_id, max_wait=600):
    """Poll Zernio for publish status"""
    for i in range(max_wait // 15):
        time.sleep(15)
        try:
            r = requests.get(
                f"https://zernio.com/api/v1/posts/{post_id}",
                headers=HEADERS_JSON,
                timeout=30,
            )
            data = r.json()
            post = data.get("post", data)
            status = post.get("status")
            plat = post.get("platforms", [{}])[0] if post.get("platforms") else {}
            ps = plat.get("status", "")
            ext = plat.get("externalPostId", "")
            err = plat.get("errorMessage", "")

            if status == "published" or ps == "published":
                return True, ext, ""
            if status == "failed" or ps in ["failed", "error"]:
                return False, "", err
        except Exception:
            pass
    return False, "", "timeout"


def build_caption(filename):
    title = (
        filename.replace("_vertical.mp4", "")
        .replace(".mp4", "")
        .replace(" - ", ": ", 1)
    )
    return f"{title}\n\n#ResurrectingBeats #Hymnmania #ChristianPsytrance #Psytrance #ElectronicMusic #WorshipMusic #HymnRemix #ElectronicWorship #2026"


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100

    posted = load_posted()
    videos = sorted([f for f in os.listdir(VERT_DIR) if f.endswith("_vertical.mp4")])
    unposted = [v for v in videos if v not in posted]

    print(f"Total: {len(videos)} | Posted: {len(posted)} | Remaining: {len(unposted)}")
    print(f"Uploading: {min(limit, len(unposted))} videos")
    print(f"Delay between posts: {POST_DELAY}s\n")

    success = 0
    failed = 0
    skipped = 0

    for i, video in enumerate(unposted[:limit]):
        video_path = VERT_DIR / video
        safe_name = safe_filename(video)

        print(f"[{i + 1}/{min(limit, len(unposted))}] {video[:60]}")

        # Step 1: Upload to Catbox
        print("  Uploading...", end=" ", flush=True)
        video_url = upload_to_catbox(video_path, safe_name)
        if not video_url:
            if os.path.getsize(video_path) / (1024 * 1024) > CATBOX_MAX_MB:
                skipped += 1
            else:
                failed += 1
            continue
        print("OK")

        # Step 2: Create Zernio post
        print("  Posting...", end=" ", flush=True)
        post = create_tiktok_post(video_url, build_caption(video))
        if not post:
            print("FAILED")
            failed += 1
            continue

        post_id = post.get("_id")
        print(f"ID={post_id[:12]}")

        # Step 3: Wait for publish
        print("  Publishing...", end=" ", flush=True)
        ok, ext_id, err = wait_for_publish(post_id)
        if ok:
            print("PUBLISHED!")
            posted[video] = {
                "post_id": post_id,
                "external_id": ext_id,
                "time": datetime.now().isoformat(),
            }
            save_posted(posted)
            success += 1
        else:
            err_short = err[:60] if err else "unknown"
            print(f"FAILED: {err_short}")
            failed += 1

            # If rate limited, wait longer
            if "rate-limited" in str(err) or "too many" in str(err).lower():
                print("  Rate limited - waiting 30 minutes...")
                time.sleep(1800)

        # Delay between posts
        if i < min(limit, len(unposted)) - 1:
            print(f"  Waiting {POST_DELAY}s...", flush=True)
            time.sleep(POST_DELAY)

    print(f"\n{'=' * 50}")
    print(f"Published: {success} | Failed: {failed} | Skipped: {skipped}")
    print(f"Total posted: {len(posted)}/{len(videos)}")


if __name__ == "__main__":
    main()
