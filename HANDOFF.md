# HANDOFF — v5.97.8 (2026-08-24)

## Critical Lessons (read before running pipeline)

1. **Full-length videos**: Use ffprobe for duration (NOT librosa — misreads VBR MP3s 40% off). Loop clips with random.choices + stream_loop. Simple concat + -shortest.

2. **Intro/outro text**: drawtext requires `fontfile=/Windows/Fonts/impact.ttf` or it segfaults silently (no text, no error).

3. **Unique thumbnails**: YouTube auto-thumbnails all look identical. Use `youtube_thumbnails.py` (random clip + text overlay per video).

4. **Quota**: 10,000 units/day shared. Rename=50, Upload=1600, Thumbnail=50, Search=100.

## Current State
- 147 beat videos (145 full-length)
- ~985 YouTube videos
- Titles fixed (179 renamed)
- Thumbnails: script ready, quota-limited (run daily)

## Posting Status
- YouTube Full + Shorts: ✅ working
- Facebook Feed + Stories: ✅ working  
- Instagram Reels: ✅ working (login @resurrectingbeats)
- TikTok: needs @resurrecting.beat login
- Facebook Reels: blocked (page access)

## Suno v4.5
- Cover flow: More → Remix (dropdown) → Cover
- Model: v4.5-all

## Relaunch Browser
`python _try_edge.py` or double-click `_open_edge.bat`
(uses --user-data-dir=C:\Users\jakeg\edge-cdp-profile to preserve logins)
