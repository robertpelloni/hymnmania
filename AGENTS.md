# HymnMania — Agent Instructions

> **Version: 5.97.5**
> **Last updated: 2026-07-29**
> **Purpose: Automated hymn/classical → electronic cover music → beat-synced video → YouTube + Facebook pipeline**
> **Status: FULLY WORKING end-to-end**

---

## CRITICAL: Spacing Rules

**Always** use proper spacing between categories in YouTube descriptions and Facebook posts:

| Category | YouTube | Facebook |
|----------|---------|----------|
| Artist | `Artist: Resurrecting Beats ft. [Author]` | — (see template) |
| Genre | `Genre: {genre_name} / Electronic Worship` | `🎹 Vibe: {genre}` |
| Year | `Year: 2026` | — |

- Use spaces around slashes: `" / "` NOT `"/"`
- Facebook uses the full `HYMNMANIA_SOCIAL_POST_TEMPLATE` structure
- YouTube uses single newlines with emoji bullets

---

## YouTube Title Format

**Hymns:** `[Genre] Hymn 2026 Remix: [Title] ([Author], [Year]) | [Speed] [Variant]`
**Classical:** `[Genre] Classical Remix - [Piece] ([Composer], [Year]) | [Speed]`

Examples:

- `Psytrance Hymn 2026 Remix: Thy Word (Amy Grant & Michael W. Smith, 1984) | 1.0x Speed [A]`
- `Dubstep Classical Remix - Canon in D (Johann Pachelbel, 1680) | Triple Speed (3.0x)`

---

## YouTube Description Template

```
Track Details:
🏷️ Artist: Resurrecting Beats ft. [Original Hymn/Author]
🎼 Track: [Song Title]
🎹 Genre: [Genre] / Electronic Worship
📅 Year: 2026
⚡ Tempo/Variant: [Speed]

About this video:
[2-3 sentences about the visual style]

🙏 Our Mission:
Welcome to Resurrecting Beats, your ultimate destination for electronic worship. Our mission is to bring the world Psytrance and other electronic genres reimagined with the hymns we have all grown to love over the years. We want to honor God by taking every hymn we can and mixing them with futuristic soundscapes. We believe that psytrance is more than just music — it's life, and a powerful vehicle for spiritual and mental elevation.

🧠 The Science of Psytrance & Healing:
We love psytrance because it profoundly engages the brain. Characterized by hypnotic, complex, and repetitive arpeggiated melodies with fast tempos (140-150+ BPM), the highly rhythmic patterns stimulate the motor cortex, while the structural build-ups and unpredictable drops activate the reward pathway, releasing dopamine.

Its driving, repetitive qualities can induce a state of "transient hypofrontality," quieting the brain's overactive analytical centers — similar to deep meditation, prayer, or non-REM sleep stages. Highly immersive music can also modulate the amygdala (the brain's emotional "almond"), helping regulate responses to stress and trauma when paired with positive stimuli or the catharsis of dancing.

While active and mindful listening to music is a scientifically proven tool that helps reduce symptoms of anxiety by lowering cortisol (the primary stress hormone) and boosting neurochemicals like serotonin, it is not a cure for clinical depression. It acts as an incredibly effective adjunctive treatment to counteract feelings of hopelessness.

*If you are experiencing depression, it is highly recommended to seek professional support. You can locate accredited therapists and mental health resources via the SAMHSA National Helpline: https://www.samhsa.gov/find-help/helplines/national-helpline*

⚙️ How We Make Our Music:
The tracks on this channel are generated and meticulously produced using Hymnmania, a custom software automation tool and orchestration platform engineered by creators Bob & Lum to fuse faith, code, and electronic music. Visuals are created using the art skills of our creators and multiple digital media tools to achieve the correct blend of the psychedelic experience.

📅 New Music Videos Uploaded Every Week.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 Business Inquiries:
Contact: ResurrectingBeats@gmail.com

🔗 Follow Our Playlists & Socials:
Facebook: https://www.facebook.com/profile.php?id=61588784931149&sk=directory_links
Instagram: https://www.instagram.com/resurrectingbeats?igsh=MWRxbGM4NHppZ2c2bw== @ResurrectingBeats
TikTok: https://www.tiktok.com/@resurrecting.beat?_r=1&_t=ZP-98NBjRbePx0

🎵 Stream/Download [Song Title]: Coming Soon

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#ResurrectingBeats #Hymnmania #ChristianPsytrance #Psytrance #ElectronicMusic #WorshipMusic #MusicTherapy #MentalHealthAwareness
```

---

## Facebook Post Template

The `daily_scheduler.py` script posts using this proven 3-step method.

### Posting Method (CRITICAL)

1. **Paste bare YouTube URL** into the composer — this triggers Facebook's link scraper to generate the video preview card
2. **Wait for preview** — poll for `img[src*=ytimg]` in the dialog, up to 20 seconds
3. **Select all + replace** — `document.execCommand('selectAll')` then `insertText` with full template text followed by the YouTube link at the bottom
4. **Wait for preview to regenerate** — Facebook re-scrapes the link after replacement
5. **Click Post** — post renders with full text structure AND video thumbnail preview card

### Post Body Template

```
{{HOOK_TEXT}} 🚀

🎵 Track: {{SONG_TITLE}}
🎹 Vibe: {{GENRE_OR_VIBE}} / Electronic Worship

{{VISUAL_EXPERIENCE_SUMMARY}} Our visuals are crafted by our creators using multiple digital media tools to deliver the ultimate psychedelic experience.

Every track is meticulously produced using Hymnmania, a custom software automation tool engineered by Bob & Lum to fuse faith, code, and electronic music. We believe psytrance is more than music — its fast, repetitive tempos stimulate the brain's reward pathways and induce a state of deep meditation and stress relief. 🙏🧠

Watch the full 4K visual journey on YouTube!

{{YOUTUBE_LINK}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#ResurrectingBeats #Hymnmania #ChristianPsytrance #Psytrance #ElectronicMusic #WorshipMusic #MusicTherapy #MentalHealthAwareness
```

### Spacing Rules

- Double newlines (`\n\n`) between EVERY section
- Space after links and hashtags
- YouTube link MUST be on its own line at the bottom for preview regeneration
- Fixed hashtag block on EVERY post — no dynamic hashtags

## Instagram Post Template

Same template as Facebook, but:

- Set `{{LINK_CTA_TEXT}}` to: `(Full 4K visual journey link in our bio! 🔗)`
- Update Instagram bio link to the YouTube video URL
- Upload MP4 video to Instagram Reels/Feed

## Instagram Credentials

- **Login**: <resurrectingbeats@gmail.com>
- **Password**: Temppass0!
- **Profile**: @ResurrectingBeats

---

## Pipeline Scripts

| Step | Script | Notes |
|------|--------|-------|
| YouTube Descriptions | `youtube_update_descriptions.py` | Artist: Resurrecting Beats ft. author |
| YouTube Title Rename | `rename_youtube_titles.py` | Standard format |
| Facebook Poster | `daily_scheduler.py` | Bare URL → preview → selectAll → full text |
| Beat Video Composer | `quick_composer.py` | ffmpeg crossfade + Magnific clips |
| Vertical Video Cropper | `vertical_video_cropper.py` | Crops 16:9 to 9:16 (1080x1920) for TikTok/Shorts |
| TikTok Uploader | `tiktok_uploader.py` | Browser automation for TikTok uploads |

---

## TikTok Pipeline

### Overview

The TikTok pipeline crops existing 16:9 horizontal videos to 9:16 vertical format and uploads them to TikTok with the same naming conventions as YouTube.

### TikTok Content Requirements

| Requirement | Specification |
|-------------|---------------|
| Format | MP4, MOV, WebM (H.264 video + AAC audio) |
| Aspect Ratio | 9:16 (1080x1920) vertical preferred |
| Duration | 3 seconds to 10 minutes (API) / 60 minutes (web) |
| AI Content | Must set `is_aigc: true` flag |
| Links | NOT clickable in captions (bio link only) |
| Caption Limit | 2200 characters max |

### Vertical Crop Workflow

```bash
# Single video
cd scripts
python vertical_video_cropper.py --input ../generated/video.mp4 --output ../generated/video_vertical.mp4

# Batch crop all hymn videos
python vertical_video_cropper.py --batch ../generated/ --outdir ../generated/vertical/
```

**Crop Logic:**

- Input: 640x360 (16:9) → Crop center 202x360 → Scale to 1080x1920
- Input: 1920x1080 (16:9) → Crop center 607x1080 → Scale to 1080x1920
- Formula: `crop_w = input_h * (9/16)`, center crop, then scale

### TikTok Upload Workflow

```bash
# Single video upload
cd scripts
python tiktok_uploader.py --video ../generated/video_vertical.mp4 --title "Psytrance Hymn 2026 Remix: Thy Word" --tags "hymn,remix,psytrance"

# Batch upload
python tiktok_uploader.py --batch ../generated/vertical/
```

**Upload Steps:**

1. Navigate to TikTok upload page
2. Upload video file via file input
3. Fill caption with title + hashtags
4. Set AIGC flag for AI-generated content
5. Click Post button

### Naming Convention (Same as YouTube)

**TikTok Caption Format:**

```
[Genre] Hymn 2026 Remix: [Title] ([Author], [Year]) | [Speed]

#ResurrectingBeats #Hymnmania #ElectronicMusic #ChristianMusic #Worship #Remix #AIMusic #HymnRemix #ElectronicWorship #2026
```

**Example:**

```
Psytrance Hymn 2026 Remix: Thy Word (Amy Grant & Michael W. Smith, 1984) | 1.0x Speed

#ResurrectingBeats #Hymnmania #ElectronicMusic #ChristianMusic #Worship #Remix #AIMusic #HymnRemix #ElectronicWorship #2026
```

### Full Pipeline (YouTube + TikTok)

```bash
# Process single video for both platforms
cd scripts
python multi_platform_pipeline.py --audio ../generated/cover.mp3 --hymn "Thy Word" --genre psytrance --speed "1.0x"

# Process all top 5 hymns
python multi_platform_pipeline.py --batch-top5
```

**Pipeline Steps:**

1. Generate beat-synced video (enhanced_video_composer.py)
2. Crop to 9:16 vertical (vertical_video_cropper.py)
3. Upload to YouTube with standard naming
4. Upload to TikTok with same naming + hashtags

### TikTok Browser State

The TikTok uploader saves browser state to `.tiktok_state.json` for persistent login. If not logged in, the script will prompt for manual login.

### Platform Comparison

| Feature | TikTok | YouTube |
|---------|--------|---------|
| Accepts Audio Only? | No (Video/Carousel only) | No (Must render to .mp4) |
| Max API Video Length | 10 Minutes | 12 Hours |
| Shorts/Vertical Spec | 9:16 (1080x1920) | 9:16 (1080x1920, ≤60 sec) |
| Clickable Links in Post | ❌ Bio link only | ✅ Description & Pinned Comment |
| Auto-Posting Obstacle | Requires TikTok App Audit | Requires YouTube API Project Quotas |
| AI Content Flag | Required (`is_aigc: true`) | Not required |

---

## Credentials

- **YouTube**: `token.json` (OAuth refreshable)
- **Facebook**: via Edge CDP browser (port 9222, profile `edge-cdp-profile`)
- **Instagram**: `resurrectingbeats@gmail.com` / `Temppass0!` (in `.secrets.json`)
- **Magnific**: `~/.env` (needs credits)
- **Channel**: Resurrecting Beats (@ResurrectingBeats)
- **Facebook Page**: <lumkourlos@gmail.com> / Page ID 61588784931149
