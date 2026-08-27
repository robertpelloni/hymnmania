# HANDOFF — v5.97.8 (2026-08-24)

## CRITICAL LESSONS (read before running pipeline)

### 1. Full-length videos (NOT clips)
- Use **ffprobe** for duration — NOT librosa (misreads Suno VBR MP3s by ~40%)
- `random.choices` (with replacement) to loop clips for long songs
- Each segment looped (`-stream_loop -1`) to exact cut_dur
- Simple concat + `-shortest`. NEVER xfade chains (collapsed videos to 11s)

### 2. Intro/outro text (drawtext)
- MUST include `fontfile=/Windows/Fonts/impact.ttf` or ffmpeg segfaults silently (no text, no error)

### 3. Unique thumbnails
- YouTube auto-thumbnails look identical. Use `youtube_thumbnails.py` (random clip + text overlay)

### 4. Titles — NEVER "cover"
- Only "Original" or "Remix" suffixes. Strip "cover" from filenames.

### 5. ≤15 hashtags ALL platforms
- YouTube/Facebook/Instagram/TikTok discard ALL hashtags if >15.
- Structure: #EDM #ResurrectingBeats #Hymnmania #SpiritualEDM #Art #Dance #LOVE #ElectronicMusic2026 + #Psytrance #PsychedelicTrance + genre + #WorshipMusic #MentalHealthAwareness #UNITY + bank tag

### 6. Facebook Reels — FIXED
- Flow: reels/create → upload → Next → Next → caption (keyboard.type) → SCROLL DOWN → click "Post" by COORDINATES
- The Post button is BELOW the fold. JS .click() on hidden button does nothing. Must mouse.click(coordinates).

### 7. Facebook link spacing
- YouTube link needs blank line BEFORE and AFTER (else preview card doesn't populate)
- The bare-URL + selectAll method caused duplicate URL. Fixed with Control+A + proper assembly.

### 8. Content originality
- MISSION_VARIATIONS (8) + reel CTAs (5) rotated per post. Never repeat same verbiage.

## Platform Status
- YouTube: Full + Shorts ✅ (Community needs 500 subs)
- Facebook: Feed + Stories + Reels ✅ (all working)
- Instagram: Reels ✅ (Create→Post flow, @resurrectingbeats)
- TikTok: needs @resurrecting.beat login

## Browser
- Relaunch: `python _try_edge.py` or double-click `_open_edge.bat`
- `--user-data-dir=C:\Users\jakeg\edge-cdp-profile` preserves all logins

## Scripts
| Script | Purpose |
|--------|---------|
| quick_composer.py | Beat videos (intro/outro + waveform visualizer + beat-sync) |
| daily_scheduler.py | Facebook feed posts (varied mission verbiage) |
| fb_stories.py | Facebook Stories + Reels (reel = scroll + coordinate click) |
| instagram_poster.py | Instagram Reels (Magnific clips + SEO captions) |
| youtube_update_descriptions.py | YouTube descriptions (≤15 hashtags) |
| rename_youtube_titles.py | YouTube titles (no "cover") |
| youtube_thumbnails.py | Unique custom thumbnails |
