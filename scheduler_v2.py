"""HymnMania Auto-Post Scheduler — v2 (verified methods 2026-09-03).

Uses ONLY the proven posting methods:
- YouTube: Data API (post_to_youtube.py) — full + shorts
- TikTok: CDP upload (tiktok.com/upload, compressed <50MB, contenteditable caption)
- Facebook Reels: fb_reel_post.py (reels/create → Create reel → Add video → set file → Next → caption → Post)
- Instagram: ig_cdp_post.py (coordinate-click New post → set file → Next → Next → Share)
- Facebook Stories: fb_stories.py story flow

Usage:
  python scheduler_v2.py --now            # run one full cycle now (test)
  python scheduler_v2.py --daemon         # run on schedule (Mon-Fri)
  python scheduler_v2.py --test           # dry-run check queue
"""
import os, sys, json, time, random, datetime, subprocess, glob, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.abspath(__file__))
BEAT_DIR = os.path.join(ROOT, "pipeline_output", "beat_videos")
SHORT_DIR = os.path.join(ROOT, "pipeline_output", "shorts")
LOG_FILE = os.path.join(ROOT, ".post_log.json")

def log_post(platform, file, url=""):
    log = []
    if os.path.exists(LOG_FILE):
        log = json.load(open(LOG_FILE))
    log.append({"time": datetime.datetime.now().isoformat(), "platform": platform, "file": file, "url": url})
    json.dump(log[-500:], open(LOG_FILE, "w"))
    print(f"  [log] {platform}: {os.path.basename(file)} {url}")

def get_queue():
    """List beat videos never posted to YouTube (checks channel titles)."""
    # Query actual channel titles once
    channel_titles = []
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        data = json.load(open(os.path.join(ROOT, "token.json")))
        creds = Credentials.from_authorized_user_info(data, ["https://www.googleapis.com/auth/youtube"])
        if not creds.valid:
            creds.refresh(Request())
        yt = build("youtube", "v3", credentials=creds)
        ch = yt.channels().list(part="contentDetails", mine=True).execute()
        upl = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        pt = None
        for _ in range(30):
            r = yt.playlistItems().list(part="snippet", playlistId=upl, maxResults=50, pageToken=pt).execute()
            for it in r.get("items", []):
                channel_titles.append(it["snippet"]["title"].lower())
            pt = r.get("nextPageToken")
            if not pt:
                break
    except Exception:
        pass
    print(f"  channel titles loaded: {len(channel_titles)}", flush=True)

    beats = sorted(f for f in os.listdir(BEAT_DIR) if f.endswith(".mp4") and not f.startswith("_"))
    pending = []
    import post_to_youtube as p
    for b in beats:
        try:
            t = p.build_title(b)
        except Exception:
            continue
        if not t:
            continue
        tl = t.lower()
        # skip if a channel title closely matches (same hymn + genre + speed)
        if any(tl.split(" Remix")[0][:30] in ct for ct in channel_titles):
            continue
        pending.append(b)
    return pending

def compress_short(src):
    """Compress to <50MB for CDP transfer. Returns path."""
    base = os.path.splitext(os.path.basename(src))[0]
    out = os.path.join(SHORT_DIR, f"{base}_tt.mp4")
    if os.path.exists(out) and os.path.getsize(out) < 50*1048576:
        return out
    FFM = r"C:\Users\jakeg\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
    r = subprocess.run([FFM, "-y", "-loglevel", "error", "-i", src,
        "-vf", "crop=ih*9/16:ih,scale=1080:1920",
        "-c:v", "libx264", "-preset", "medium", "-crf", "26", "-b:v", "4M",
        "-c:a", "aac", "-b:a", "128k", "-t", "60", out], capture_output=True)
    return out if os.path.exists(out) else None

def make_tt_caption(title, genre):
    return f"""🌀 RESURRECTING BEATS: '{title}' [{genre}] ⚡

Resurrected from the vault! Full genre-mixed hymn cover — {genre} electronic worship. Built for festivals, vocalists, and live sets.

🎧 Full 4K video on YouTube (link in bio)!
💬 Comment '{title.upper()[:12]}' for the untagged high-quality link.

#ResurrectingBeats #EDM #SpiritualEDM #ElectronicMusic #HymnMania #producertok #edmmusic #trancefamily #festivalbeats #{genre.replace(' ','')} #dance"""

def post_youtube_full(beat_file, title, genre):
    """YouTube full video via API."""
    import post_to_youtube as p
    service = p.get_service()
    src = os.path.join(BEAT_DIR, beat_file)
    vid = p.upload(service, src, p.build_title(beat_file))
    log_post("youtube-full", beat_file, f"https://youtu.be/{vid}")
    # record as uploaded
    with open(os.path.join(ROOT, ".uploaded_videos.txt"), "a") as f:
        f.write(f"{vid} | {os.path.basename(beat_file)}\n")
    return vid

def post_tiktok(video_path, caption):
    """Verified TikTok upload via CDP."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = next((p for p in b.contexts[0].pages if "tiktok.com" in p.url), None)
        if not page:
            page = b.contexts[0].new_page()
        page.goto("https://www.tiktok.com/upload", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(6000)
        try:
            page.click('[data-e2e="select_video_button"]', timeout=8000)
        except Exception:
            page.evaluate("Array.from(document.querySelectorAll('button')).find(x=>/select video/i.test(x.innerText||''))?.click()")
        page.wait_for_timeout(2000)
        abs_path = os.path.abspath(video_path)
        page.set_input_files('[data-e2e="upload-input"],input[type=file]', abs_path, timeout=90000)
        for _ in range(25):
            page.wait_for_timeout(3000)
            body = page.evaluate("document.body.innerText")
            if "uploaded" in body.lower() and "description" in body.lower():
                break
        page.wait_for_timeout(2000)
        page.evaluate("document.querySelector('[contenteditable=true]')?.focus()")
        page.wait_for_timeout(500)
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        page.keyboard.type(caption, delay=4)
        page.wait_for_timeout(2500)
        r = page.evaluate("(()=>{var b=document.querySelector('[data-e2e=post_video_button]');if(b){b.scrollIntoView({block:'center'});b.click();return 'ok'}return 'nf'})()")
        page.wait_for_timeout(8000)
        b.close()
        return r == "ok"

def post_instagram(beat_path, title, genre, yt):
    """Verified IG via CDP coordinate-click."""
    import ig_cdp_post as ig
    cap = f"🌀 RESURRECTING BEATS: '{title}' [{genre}]\n\n🎵 {genre} electronic worship remix — full genre-mixed hymn cover.\n\n👍 Like + Subscribe — full 4K journey on YouTube (link in bio): {yt}\n\n#ResurrectingBeats #Hymnmania #SpiritualEDM #{genre.replace(' ','')} #EDM #ElectronicMusic"
    capfile = os.path.join(ROOT, ".ig_auto_cap.txt")
    io.open(capfile, "w", encoding="utf-8").write(cap)
    return ig.post(beat_path, capfile)

def post_fb_reel(video_path, title, genre, yt):
    """Best-effort FB reel via fb_reel_post.py subprocess; falls back to FB feed post.
    Facebook intermittently redirects reels/create to a reel viewer, so reel may fail
    — the feed post fallback is the reliable path."""
    try:
        import subprocess as _sp
        r = _sp.run([sys.executable, os.path.join(ROOT, "fb_reel_post.py"),
                     os.path.abspath(video_path), title, genre, yt or ""],
                    capture_output=True, timeout=280)
        out = (r.stdout or b"").decode("utf-8", errors="replace")
        if "RESULT: True" in out or "Reel posted" in out:
            return True
        print(f"  FB reel subprocess no-success — trying feed post", flush=True)
    except Exception as e:
        print(f"  FB reel error: {str(e)[:50]} — trying feed post", flush=True)
    # Fallback: FB feed post (reliable)
    try:
        from daily_scheduler import build_post, post_to_facebook
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
            fb = b.contexts[0].new_page()
            fb.goto("https://www.facebook.com/")
            fb.wait_for_timeout(6000)
            post_text, _ = build_post(os.path.basename(video_path), title, genre)
            post_to_facebook(fb, post_text, yt)
            b.close()
        print("  FB feed post OK", flush=True)
        return True
    except Exception as e:
        print(f"  FB feed post FAIL: {str(e)[:50]}", flush=True)
        return False

def cycle_one(beat_file=None):
    """Post one beat video across all platforms."""
    queue = get_queue()
    if not beat_file:
        if not queue:
            print("No pending beat videos (all posted to YouTube)")
            return
        beat_file = queue[0]
    print(f"\n=== Posting: {beat_file} ===")
    import post_to_youtube as p
    title_full = p.build_title(beat_file) or beat_file
    genre = title_full.split()[0]
    title = "Jesus Comes With Power" if "Jesus" in beat_file else beat_file.replace("_", " ").split("_cover")[0]

    # 0. Build compressed 9:16 short ONCE for TikTok/FB/IG (must be <50MB for CDP)
    short = compress_short(os.path.join(BEAT_DIR, beat_file))
    print(f"  compressed short: {short}", flush=True)

    # 1. YouTube full
    vid = None
    try:
        vid = post_youtube_full(beat_file, title, genre)
        print(f"  YouTube OK: {vid}")
    except Exception as e:
        print(f"  YouTube FAIL: {str(e)[:60]}")

    # 2. TikTok (compressed short)
    try:
        if short:
            cap = make_tt_caption(title, genre)
            ok = post_tiktok(short, cap)
            print(f"  TikTok {'OK' if ok else 'FAIL'}")
    except Exception as e:
        print(f"  TikTok FAIL: {str(e)[:60]}")

    # 3. Facebook reel (best-effort, falls back to feed)
    try:
        if short:
            ok = post_fb_reel(short, title, genre, f"https://youtu.be/{vid}" if vid else "")
            print(f"  FB {'OK' if ok else 'FAIL (intermittent)'}")
    except Exception as e:
        print(f"  FB FAIL: {str(e)[:60]}")

    # 4. Instagram (compressed short)
    try:
        if short:
            ok = post_instagram(short, title, genre, f"https://youtu.be/{vid}" if vid else "")
            print(f"  Instagram {'OK' if ok else 'FAIL'}")
    except Exception as e:
        print(f"  Instagram FAIL: {str(e)[:60]}")

def run_cycle(count=1):
    for _ in range(count):
        cycle_one()

if __name__ == "__main__":
    if "--test" in sys.argv:
        q = get_queue()
        print(f"Queue: {len(q)} pending beat videos")
        for x in q[:10]:
            print("  ", x)
    elif len(sys.argv) > 1 and sys.argv[1].isdigit():
        run_cycle(int(sys.argv[1]))
    else:
        run_cycle(1)
