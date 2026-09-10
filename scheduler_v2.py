"""HymnMania unified scheduler — posts ONE ready track across all platforms.

Uses ONLY the verified flows (2026-09-10):
  YouTube full + Short : post_to_youtube.py (API, quality-gated)
  TikTok               : tt_post.post_video   (port 9222, handles 'Post now' modal)
  Facebook Reel        : fb_reel_post.py      (waits for copyright check to clear)
  Instagram Reel       : ig_cdp_post.post     (keyboard.type caption BEFORE Share)
  Facebook feed (opt)  : daily_scheduler      (link post fallback)

Browser split (IMPORTANT):
  9222 / edge-cdp-profile  -> Facebook, Instagram, TikTok (social logins)
  9333 / .dedicated-edge-profile -> Suno only (cover generation)

Usage:
  python scheduler_v2.py --test        # dry run: show the queue
  python scheduler_v2.py --now         # post the next ready track everywhere
  python scheduler_v2.py --now 3       # post the next 3 tracks
  python scheduler_v2.py --daemon      # run one cycle per day at RUN_HOUR (weekdays)
"""
import os, sys, json, io, time, random, datetime, subprocess, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
BEAT_DIR = os.path.join(ROOT, "pipeline_output", "beat_videos")
SHORT_DIR = os.path.join(ROOT, "pipeline_output", "shorts")
LOG_FILE = os.path.join(ROOT, ".scheduler_log.json")
SOCIAL_PORT = 9222
RUN_HOUR = 15          # 3 PM local
QUALITY_THRESHOLD = 1000

FFM = r"C:\Users\jakeg\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"


# ---------------------------------------------------------------- logging
def load_log():
    if os.path.exists(LOG_FILE):
        try:
            return json.load(open(LOG_FILE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_log(log):
    json.dump(log, open(LOG_FILE, "w", encoding="utf-8"), indent=1)


def mark(beat_file, platform, url=""):
    log = load_log()
    e = log.setdefault(beat_file, {"posted": [], "urls": {}})
    if platform not in e["posted"]:
        e["posted"].append(platform)
    if url:
        e["urls"][platform] = url
    save_log(log)


def already(beat_file, platform):
    return platform in load_log().get(beat_file, {}).get("posted", [])


# ---------------------------------------------------------------- quality
def spectral_centroid(f, seconds=25):
    import numpy as np, tempfile
    tmp = tempfile.mktemp(suffix=".f32")
    subprocess.run([FFM, "-y", "-loglevel", "error", "-i", f, "-t", str(seconds),
                    "-ac", "1", "-ar", "48000", "-f", "f32le", tmp], capture_output=True)
    d = np.frombuffer(open(tmp, "rb").read(), dtype=np.float32)
    os.remove(tmp)
    cents = []
    for i in range(0, len(d) - 2048, 2048):
        sp = np.abs(np.fft.rfft(d[i:i + 2048] * np.hanning(2048)))
        fr = np.fft.rfftfreq(2048, 1 / 48000)
        if sp.sum() > 0:
            cents.append((sp * fr).sum() / sp.sum())
    return round(float(np.mean(cents)), 1) if cents else 0


def is_real_cover(beat_file):
    c = spectral_centroid(os.path.join(BEAT_DIR, beat_file))
    return c >= QUALITY_THRESHOLD, c


def not_looped(path):
    """False if the 48s-repeat capture bug is present."""
    try:
        import cap_cycle
        tmp = os.path.join(SHORT_DIR, "_gatecheck.mp3")
        subprocess.run([FFM, "-y", "-loglevel", "error", "-i", path, "-ac", "1",
                        "-ar", "48000", tmp], capture_output=True)
        ls = cap_cycle.loop_score(tmp)
        os.remove(tmp)
        return ls <= 0.9, ls
    except Exception:
        return True, 0.0


def is_short(path):
    """True if the video is <=70s (already a short, don't make another)."""
    try:
        FFP = os.path.join(os.path.dirname(FFM), "ffprobe.exe")
        r = subprocess.run([FFP, "-v", "quiet", "-show_entries", "format=duration",
                            "-of", "csv=p=0", path], capture_output=True, text=True)
        return float(r.stdout.strip() or 0) <= 70
    except Exception:
        return False


# ---------------------------------------------------------------- queue
def channel_titles():
    try:
        import post_to_youtube as p
        yt = p.get_service()
        ch = yt.channels().list(part="contentDetails", mine=True).execute()
        upl = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        titles, pt = set(), None
        for _ in range(60):
            r = yt.playlistItems().list(part="snippet", playlistId=upl,
                                        maxResults=50, pageToken=pt).execute()
            for it in r.get("items", []):
                titles.add(it["snippet"]["title"].lower().replace(" #shorts", ""))
            pt = r.get("nextPageToken")
            if not pt:
                break
        return titles
    except Exception as e:
        print(f"  (channel lookup failed: {str(e)[:50]})")
        return set()


def get_queue(verbose=True):
    """Full-length, real-audio, non-looped beat videos never posted to YouTube."""
    import post_to_youtube as p
    posted = channel_titles()
    log = load_log()
    queue = []
    for b in sorted(os.listdir(BEAT_DIR)):
        if not b.endswith(".mp4") or b.startswith("_"):
            continue
        path = os.path.join(BEAT_DIR, b)
        if is_short(path):
            continue
        try:
            t = p.build_title(b)
        except Exception:
            t = None
        if not t or t.lower() in posted:
            continue
        if "youtube-full" in log.get(b, {}).get("posted", []):
            continue
        ok, c = is_real_cover(b)
        if not ok:
            if verbose:
                print(f"  skip (sine/sheet-music, centroid={c}): {b[:50]}")
            continue
        good, ls = not_looped(path)
        if not good:
            if verbose:
                print(f"  skip (48s-loop bug, score={ls}): {b[:50]}")
            continue
        queue.append(b)
    if verbose:
        print(f"  queue: {len(queue)} ready track(s)")
    return queue


# ---------------------------------------------------------------- platforms
def make_and_compress_short(beat_file):
    """9:16 60s short, compressed under the 50MB CDP limit."""
    import post_to_youtube as p
    src = os.path.join(BEAT_DIR, beat_file)
    base = os.path.splitext(beat_file)[0]
    raw = os.path.join(SHORT_DIR, base + "_short.mp4")
    if not (os.path.exists(raw) and os.path.getsize(raw) > 100000):
        raw = p.make_short(src, raw)
    if not raw or not os.path.exists(raw):
        return None
    out = os.path.join(SHORT_DIR, base + "_short_compressed.mp4")
    if os.path.exists(out) and os.path.getsize(out) < 50 * 1048576:
        return out
    r = subprocess.run([FFM, "-y", "-loglevel", "error", "-i", raw,
                        "-c:v", "libx264", "-preset", "fast", "-crf", "28",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
                       capture_output=True)
    if os.path.exists(out) and os.path.getsize(out) < 50 * 1048576:
        return out
    return raw


def post_youtube(beat_file, is_short=False):
    import post_to_youtube as p
    src = os.path.join(BEAT_DIR, beat_file)
    title = p.build_title(beat_file)
    # quality gate (same check the CLI uses)
    if not p.quality_gate(src):
        raise RuntimeError("quality gate failed (looped capture)")
    svc = p.get_service()
    if is_short:
        base = os.path.splitext(beat_file)[0]
        out = os.path.join(SHORT_DIR, base + "_short.mp4")
        if not (os.path.exists(out) and os.path.getsize(out) > 100000):
            out = p.make_short(src, out)
        vid = p.upload(svc, out, title, is_short=True)
    else:
        vid = p.upload(svc, src, title)
    mark(beat_file, "youtube-short" if is_short else "youtube-full", f"https://youtu.be/{vid}")
    return vid


def post_tiktok(short_path, beat_file, title, genre):
    from playwright.sync_api import sync_playwright
    import tt_post
    cap = (f"\U0001f300 RESURRECTING BEATS: '{title}' [{genre} / Spiritual EDM] \u26a1\n\n"
           f"Resurrected from the vault! High-energy {genre} energy. Built for festivals, "
           f"vocalists, and live sets.\n\n"
           f"\U0001f3a7 Free Download / License link in bio!\n"
           f"\U0001f4ac Comment '{title.upper()[:14]}' for the untagged link.\n\n"
           f"#ResurrectingBeats #EDM #{genre.replace(' ', '')} #SpiritualEDM #ElectronicMusic "
           f"#Dance #HymnMania #producertok #edmmusic #trancefamily #festivalbeats #unreleasedmusic")
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{SOCIAL_PORT}")
        page = b.contexts[0].new_page()
        ok = tt_post.post_video(page, os.path.abspath(short_path), cap)
        b.close()
    return ok


def post_fb_reel(short_path, title, genre, yt):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "fb_reel_post.py"),
                        os.path.abspath(short_path), title, genre, yt or ""],
                       capture_output=True, timeout=420)
    out = (r.stdout or b"").decode("utf-8", errors="replace")
    return ("RESULT: True" in out) or ("published: True" in out) or ("shared with everyone" in out.lower())


def post_instagram(short_path, title, genre, yt):
    import ig_cdp_post as ig
    cap = (f"{title} \u2014 {genre} electronic worship\n\n"
           f"Can this {genre} frequency elevate your spirit? \U0001f447 Drop a like and tell us below!\n\n"
           f"(Full 4K visual journey link in our bio! \U0001f517)\n\n"
           f"#ResurrectingBeats #Hymnmania #SpiritualEDM #{genre.replace(' ', '')} #EDM "
           f"#ElectronicMusic #PsychedelicTrance #WorshipMusic")
    capfile = os.path.join(ROOT, ".ig_auto_cap.txt")
    io.open(capfile, "w", encoding="utf-8").write(cap)
    return ig.post(os.path.abspath(short_path), capfile)


def ensure_browser(port=SOCIAL_PORT, profile=r"C:\Users\jakeg\edge-cdp-profile"):
    """Launch the browser for the social logins if CDP is not already up."""
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=4)
        return True
    except Exception:
        pass
    print(f"  launching browser on {port}...", flush=True)
    try:
        subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                          f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
                          "--no-first-run", "--no-default-browser-check",
                          "--disable-features=msEdgeDisableStartupBoost"])
    except Exception as e:
        print(f"  browser launch failed: {str(e)[:60]}")
        return False
    for _ in range(20):
        time.sleep(2)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=3)
            print("  browser ready")
            return True
        except Exception:
            pass
    return False


# ---------------------------------------------------------------- cycle
def nice_title(beat_file):
    import post_to_youtube as p
    t, a, y, cls, g, sp, var = p.detect(beat_file)
    return t or beat_file.replace("_", " ")


def cycle_one(beat_file=None):
    if beat_file is None:
        q = get_queue()
        if not q:
            print("Nothing to post — queue empty.")
            return False
        beat_file = q[0]
    title = nice_title(beat_file)
    import post_to_youtube as p
    t, a, y, cls, genre, sp, var = p.detect(beat_file)
    genre = genre or "Psytrance"
    print(f"\n=== {title} ({genre}) ===")

    yt_url = ""
    for name, fn in [
        ("youtube-full", lambda: post_youtube(beat_file, False)),
        ("youtube-short", lambda: post_youtube(beat_file, True)),
    ]:
        if already(beat_file, name):
            print(f"  {name}: already done")
            continue
        try:
            vid = fn()
            print(f"  {name}: OK https://youtu.be/{vid}")
            if name == "youtube-full":
                yt_url = f"https://youtu.be/{vid}"
        except Exception as e:
            print(f"  {name}: FAIL {str(e)[:70]}")

    short = make_and_compress_short(beat_file)
    print(f"  short: {short}")
    if not short:
        print("  no short clip — skipping socials")
        return True

    if not ensure_browser():
        print("  social browser unavailable — YouTube only this run")
        return True

    if yt_url and not already(beat_file, "fb-feed"):
        try:
            from daily_scheduler import build_post, post_to_facebook
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{SOCIAL_PORT}")
                fb = b.contexts[0].new_page()
                fb.goto("https://www.facebook.com/", wait_until="domcontentloaded")
                fb.wait_for_timeout(6000)
                post_text, _ = build_post(os.path.basename(short), title, genre)
                post_to_facebook(fb, post_text, yt_url)
                b.close()
            mark(beat_file, "fb-feed", yt_url)
            print("  fb-feed: OK")
        except Exception as e:
            print(f"  fb-feed: FAIL {str(e)[:60]}")

    for name, fn in [
        ("tiktok", lambda: post_tiktok(short, beat_file, title, genre)),
        ("fb-reel", lambda: post_fb_reel(short, title, genre, yt_url)),
        ("instagram", lambda: post_instagram(short, title, genre, yt_url)),
    ]:
        if already(beat_file, name):
            print(f"  {name}: already done")
            continue
        try:
            ok = fn()
            mark(beat_file, name, "ok" if ok else "")
            print(f"  {name}: {'OK' if ok else 'FAIL'}")
        except Exception as e:
            print(f"  {name}: FAIL {str(e)[:70]}")
    return True


def run_cycle(count=1):
    n = 0
    for _ in range(count):
        try:
            if cycle_one():
                n += 1
            else:
                break
        except Exception as e:
            print(f"cycle error: {str(e)[:80]}")
    print(f"\nCompleted {n} cycle(s).")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--test" in args:
        get_queue(verbose=False)
        q = get_queue()
        for b in q[:15]:
            import post_to_youtube as p
            print("  ", p.build_title(b))
    elif "--daemon" in args:
        print(f"daemon: posting one track/day on weekdays at {RUN_HOUR}:00")
        done_day = None
        while True:
            now = datetime.datetime.now()
            if now.weekday() < 5 and now.hour == RUN_HOUR and done_day != now.date():
                run_cycle(1)
                done_day = now.date()
            time.sleep(300)
    else:
        count = 1
        for a in args:
            if a.isdigit():
                count = int(a)
        run_cycle(count)
