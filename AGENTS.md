# HymnMania — Agent Instructions

> **Version: 5.97.8**
> **Last updated: 2026-08-05**
> **Purpose: Automated hymn/classical → electronic cover music → beat-synced video → YouTube + Facebook pipeline**
> **Status: FULLY WORKING end-to-end**

---

## CRITICAL: 15-Hashtag Limit (ALL PLATFORMS)

YouTube, Facebook, Instagram, and TikTok all DISREGARD every hashtag if a single post exceeds 15. NEVER exceed 15 combined hashtags on ANY platform.

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

**CRITICAL**: NEVER put "cover" in the title. Only acceptable suffixes are "Original" or "Remix". Strip "cover" from filenames when generating titles.

**Genre Detection**: When the title doesn't contain the genre keyword, the rename script extracts it from the YouTube description (`Genre: {genre} / Electronic Worship`). If still unknown, use the placeholder `[EDM LSDance]` (case-sensitive, exact format). Never use "Electronic" alone as a genre in titles.

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
#EDM #ResurrectingBeats #Hymnmania #SpiritualEDM #Art #Dance #LOVE #ElectronicMusic2026 #Psytrance #PsychedelicTrance #[Genre] #WorshipMusic #MentalHealthAwareness #UNITY + 1-2 bank tags (MAX 15 TOTAL)
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
#ResurrectingBeats #Hymnmania #SpiritualEDM #Psytrance #ElectronicMusic #WorshipMusic #MusicTherapy #MentalHealthAwareness
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

- **Login**: resurrectingbeats@gmail.com
- **Password**: Temppass0!
- **Profile**: @ResurrectingBeats

---

## Pipeline Scripts

| Step | Script | Notes |
|------|--------|-------|
| YouTube Descriptions | `youtube_update_descriptions.py` | Artist: Resurrecting Beats ft. author |
| YouTube Title Rename | `rename_youtube_titles.py` | Standard format |
| Facebook Poster | `daily_scheduler.py` | Bare URL → preview → selectAll → full text |
| Facebook Stories | `fb_stories.py` | Compressed 9:16 clip → Stories upload with YT link |
| Beat Video Composer | `quick_composer.py` | ffmpeg concat + Magnific clips + intro/outro + thumbnails (full-length) |
| Cover Generator | `batch_cover_gen.py` | Suno v4.5 More→Remix→Cover flow |
| YouTube Shorts | `shorts_composer.py` | 9:16 vertical 60s clips from beat videos |
| YouTube Community | CDP browser | Static SEO posts on Community tab (requires 500+ subscribers) |
| TikTok Poster | `tiktok_poster.py` | Convert to vertical + upload via CDP browser |
| Scheduler Bot | `scheduler_bot.py` | Weekly auto-posting Mon-Fri to TikTok + Facebook |
| AI Metadata | Embedded JSON-LD | Schema.org MusicRecording for AI crawler indexing |

## Beat Video Branding

### Beat Synchronization
Every video is beat-synced to the music with tempo-scaled phrase lengths:
1. **librosa** detects BPM from the audio track (range 60-200 BPM)
2. Clip duration scales with tempo to keep cuts in the 3-6 second sweet spot:

| Tempo Range | Beats/Phrase | Clip Duration | Genres |
|------------|-------------|---------------|--------|
| >160 BPM | 16 beats | ~5-6s | Gabba, fast DnB |
| 130-160 BPM | 12 beats | ~4.5-5.5s | Psytrance, Hardstyle |
| 100-130 BPM | 8 beats | ~3.7-4.8s | Deep House, Detroit, Dubstep |
| <100 BPM | 4 beats | ~2.4-4s | Half-speed, ambient |

### Intro/Outro (Text on Video — REQUIRES fontfile)
- **Intro (2.5s)**: "RESURRECTING BEATS" + genre name over random Magnific clip with genre-matched colors
- **Outro (3s)**: "RESURRECTING BEATS" + "Subscribe for more!" with fade-out
- **CRITICAL**: drawtext MUST include `fontfile=/Windows/Fonts/impact.ttf` — without it, ffmpeg segfaults and the text silently fails to render

### Genre Style Map
| Genre | Text Color | Effect |
|-------|-----------|--------|
| Psytrance | Purple neon | Neon glow |
| Dubstep | Red | Bass shake |
| Deep House | Gold | Warm fade |
| Drum and Bass | Cyan | Fast pulse |
| Chiptune | Lime green | Pixel glitch |
| Gabba | Orange | Hardcore flash |
| Detroit Techno | Silver | Industrial |
| Detroit House | Gold | Smooth |
| Hardstyle Trance | Yellow | Laser blast |
| Synthwave | Magenta | Neon grid |
| Japanese Hardcore | Cyan | Kawaii rave |

### Unique Previews
- Clips are randomly sampled from 152 Magnific videos
- Each clip uses a random start timestamp — no two videos start the same way
- YouTube thumbnail frames are always different

## TikTok Posting

### Channel
- **Handle**: @resurrecting.beat
- **URL**: https://www.tiktok.com/@resurrecting.beat?_r=1&_t=ZP-98NBjRbePx0

### Post Template
```
🌀 RESURRECTING BEATS: '{TRACK_TITLE}' [{SUB_GENRE}] ⚡

Resurrected from the vault! {VIBE} energy at {BPM} BPM in {KEY}. Built for festivals, vocalists, and live sets.

🎧 Free Download / License link in bio!
💬 Comment '{TRACK_TITLE_UPPER}' for the untagged high-quality link.

#ResurrectingBeats #EDM #Psytrance #SpiritualEDM #ElectronicMusic #Dance #DanceSafe #HymnMania

#producertok #edmmusic #trancefamily #festivalbeats #unreleasedmusic #[Genre] #[Hook/TrackTitle]
```

### Example
```
🌀 RESURRECTING BEATS: 'Samsara' [Psytrance / Spiritual EDM] ⚡

Resurrected from the vault! High-energy 138 BPM Psytrance beat packed with spiritual vocals & driving bass. Perfect for festivals, vocalists, and content creators.

🎧 Free Download / License link in bio!
💬 Comment 'SAMSARA' to get the untagged high-quality link sent to your inbox.

#ResurrectingBeats #EDM #Psytrance #SpiritualEDM #ElectronicMusic #Dance #DanceSafe #HymnMania #producertok #trancefamily #festivalmusic #unreleasedmusic #producertok #edmbeats
```

### Posting Method
- **Upload**: TikTok web uploader at `tiktok.com/upload` via CDP browser
- **Format**: 9:16 vertical (1080x1920) MP4 — converted from existing beat videos
- **Privacy**: PUBLIC_TO_EVERYONE
- **AI flag**: Set `is_aigc=true` for Suno-generated audio

### What's Needed to Post
1. CDP browser session with TikTok logged in (@resurrecting.beat)
2. 9:16 vertical video files (converted via ffmpeg crop/scale from beat videos)
3. BPM + Key metadata (extracted via librosa)
4. TikTok web uploader automation script (same pattern as Facebook poster)

## Credentials

- **YouTube**: `token.json` (OAuth refreshable)
- **Facebook**: via Edge CDP browser (port 9222, profile `edge-cdp-profile`)
- **Instagram**: `resurrectingbeats@gmail.com` / `Temppass0!` (in `.secrets.json`)
- **Magnific**: `~/.env` (needs credits)
- **Channel**: Resurrecting Beats (@ResurrectingBeats)
- **Facebook Page**: lumkourlos@gmail.com / Page ID 61588784931149

## Growth Recommendations

### Immediate (can implement now)
| Priority | Feature | Impact | Effort |
|----------|---------|--------|--------|
| **P0** | Crossfade transitions between clips (0.3-0.5s xfade) | High | Low |
| **P0** | YouTube Shorts - 60s vertical highlights from beat videos | High | Medium |
| **P0** | End screens - Subscribe + next video card on last 20s | High | Low |
| **P1** | Custom thumbnails - genre + hymn title overlay | Medium | Medium |
| **P1** | Audio-reactive waveform/spectrum overlay synced to beat | Medium | Medium |
| **P1** | Playlist auto-organization by hymn, genre, speed | Medium | Low |
| **P1** | TikTok/Reels cross-post - 9:16 vertical cuts | High | Medium |
| **P2** | Comment auto-engagement - reply with YT link | Low | Low |
| **P2** | Ken Burns zoom/pan on static clips | Medium | Low |
| **P2** | Pinned comment: "Which hymn should we remix next?" | Low | Low |

### Weekly Cadence
| Day | Time (EST) | Content Type | Platform |
|-----|-----------|-------------|----------|
| MON | 3-5 PM | HOOK_DROP (15s loop) | TikTok + FB |
| TUE | 2-6 PM | VAULT_STORY (30s background) | TikTok + FB |
| WED | 1-6 PM | HOOK_DROP (15s loop) | TikTok + FB |
| THU | 1-5 PM | CONVERSION (30s YT promo) | TikTok + FB |
| FRI | 3-5 PM | HOOK_DROP (15s loop) | TikTok + FB |
| SAT/SUN | — | Rest / Queue Reset | — |

Run manually: `python scheduler_bot.py HOOK_DROP`
Auto-run: leave running and it posts on schedule hourly check

### Subscriber Hooks
- **First 3s**: RESURRECTING BEATS intro flash
- **Last 20s**: End screen with subscribe CTA
- **Description**: Clear call-to-action to subscribe
- **Cross-promote**: Link Facebook + TikTok in every description

### YouTube Post Types (All 3)
| Type | Format | Method | Min Subs |
|------|--------|--------|----------|
| Full Video | 16:9 MP4 | API videos().insert() | 0 |
| Shorts | 9:16 vertical <60s | API + #Shorts tag | 0 |
| Community (Static) | Text + link | CDP browser Community tab | 500 |

Community tab blocked until 500 subscribers. Script ready.

### Facebook Stories & Reels
- **Script**: `fb_stories.py` — creates 20s compressed 9:16 clips from beat videos
- **Upload**: CDP browser → `facebook.com/stories/create`
- **Format**: 9:16 vertical (720x1280), under 50MB, 15-30 second clips
- **Headline**: Track title + genre + YouTube link
- **Link**: Full YouTube URL included in the story text

## Facebook — All Post Types

### 1. Feed Posts (`daily_scheduler.py`)
- Text + YouTube link in body (generates video preview card)
- Full template: hook, track, vibe, visual summary, Hymnmania production, YT link
- Method: bare URL → preview → selectAll + replace → Post
- Hashtags: #ResurrectingBeats #Hymnmania #SpiritualEDM #Psytrance #ElectronicMusic #WorshipMusic #MusicTherapy #MentalHealthAwareness

### 2. Stories (`fb_stories.py`)
- 20-second 9:16 vertical clip from beat video
- Compressed to ~5MB (under CDP 50MB limit)
- Text overlay: track name + resurrectingbeats + genre (via ffmpeg drawtext with fontfile)
- Upload via CDB `facebook.com/stories/create`
- Stays live 24 hours

### 3. Reels (`fb_stories.py` — `post_to_facebook_reel`)
- Flow DISCOVERED: facebook.com/reels/create → upload → Next → Next → caption → Post
- Caption field: placeholder "Describe your reel..." (use keyboard.type, NOT execCommand)
- Final button: "Post" (not Publish/Share)
- **STATUS**: Draft created but final publish not confirmed (reel shows "No reels yet")
- Instagram Reels WORK (verified 4 posts). Facebook Reels still need the final publish step resolved.

### Hashtag Block (ALL Facebook Posts)
```
#ResurrectingBeats #Hymnmania #SpiritualEDM #Psytrance #ElectronicMusic #WorshipMusic #MusicTherapy #MentalHealthAwareness
```
Plus genre-specific: #Dubstep #DeepHouse #DrumAndBass #Chiptune #Gabba #DetroitTechno #DetroitHouse #Hardstyle #Synthwave #JapaneseHardcore

## Instagram Posting (UPDATED 2026-08-24)
- **Script**: `instagram_poster.py` — use `post_beat_to_instagram()` (NOT `post_magnific_clip`)
- **Video**: Beat videos (have AUDIO + RESURRECTING BEATS intro), converted to 9:16 30s Reel
- **Flow**: instagram.com → Create ("New post") → "Post" → upload → Next → Next → caption → Share
- **Caption**: Sound description (genre + BPM) + like/subscribe CTA + YouTube link + <=15 hashtags
- **Credentials**: resurrectingbeats@gmail.com / Temppass0! (in .secrets.json)
- **CRITICAL**: Use beat videos (have audio+intro), NOT raw Magnific clips (silent, no intro)

## Suno v4.5 Cover Flow (Updated 2026-08-19)

Suno UI changed from v5.5 → v4.5. The Cover flow is now:
- **Old**: More menu → Remix → Cover (nested)
- **New**: More menu (three dots) → Remix (opens dropdown) → **Cover**

Cover still opens at `suno.com/create` with the song as reference and v4.5-all model. Same genre/style injection as before.

### Full-Length Video Guarantee (CRITICAL)
The beat composer uses **ffprobe** duration (NOT librosa — librosa misreads Suno VBR MP3s by ~40%):
1. ffprobe reads true audio duration
2. `random.choices` loops Magnific clips for long songs
3. Each clip looped (`-stream_loop`) to exact cut_dur
4. Simple concat + `-shortest` cuts at full song end

Verification: 135 beat videos, 0 truncated, 0 empty, all match source audio.

## How To Relaunch The Edge CDP Browser

When the browser closes, run one of these methods:

### Method 1: Script (easiest)
```bash
python _try_edge.py
```

### Method 2: Command line (manual)
```cmd
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir=C:\Users\jakeg\edge-cdp-profile --no-first-run --no-default-browser-check
```

### Method 3: Batch file
Create `_open_edge.bat` with:
```bat
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir=C:\Users\jakeg\edge-cdp-profile --no-first-run --no-default-browser-check
```

**IMPORTANT**: The `--user-data-dir=C:\Users\jakeg\edge-cdp-profile` is what preserves all your logins (Facebook, Instagram, Suno, Magnific). ALWAYS include it or you'll lose sessions.

## CRITICAL: Beat Video & Thumbnail Rules (Learned 2026-08-24)

### 1. Full-Length Videos (NOT clips)
- Use **ffprobe** for duration — NOT librosa (librosa misreads Suno VBR MP3s by ~40%)
- `random.choices` (with replacement) to loop Magnific clips for long songs
- Each segment looped (`-stream_loop -1`) to exact `cut_dur`
- Simple concat + `-shortest` cuts at full song end
- NEVER use xfade chains — the offset math collapsed videos to 11s

### 2. Intro/Outro Text (drawtext)
- drawtext MUST include `fontfile=/Windows/Fonts/impact.ttf` 
- WITHOUT fontfile, ffmpeg segfaults and text silently fails (no error, no text)
- Intro (2.5s): "RESURRECTING BEATS" + genre name
- Outro (3s): "RESURRECTING BEATS" + "Subscribe for more!"

### 3. Unique Thumbnails (NO duplicates)
- YouTube auto-thumbnails from first frame = all look identical (similar Magnific clips)
- Fix: `youtube_thumbnails.py` generates custom thumbnails
- Each thumbnail = UNIQUE random Magnific clip + genre + hymn text overlay
- Run daily: `python youtube_thumbnails.py 100` (quota ~200/day)

### 4. Quota Management
- YouTube Data API = 10,000 units/day (SHARED pool)
- Title rename = 50 units, Upload = 1,600 units, Thumbnail = 50 units, Search = 100 units
- Plan order: uploads first → titles → thumbnails last
- Never exceed ~200 renames/day (10,000 units / 50)

### 5. Beat Sync (librosa for BPM only)
- librosa is GOOD for BPM detection (tempo)
- librosa is BAD for duration (VBR misread)
- tempo-scaled beats: >160 BPM=16 beats, 130-160=12, 100-130=8, <100=4

## Hashtag Rules (CRITICAL — YouTube ignores ALL hashtags if >15)

### Max 15 Combined Hashtags Per Post
YouTube discards ALL hashtags if a description contains more than 15. NEVER exceed 15.

### Structure (always in this order)
1. **Core (8)**: #EDM #ResurrectingBeats #Hymnmania #SpiritualEDM #Art #Dance #LOVE #ElectronicMusic2026
2. **Psytrance (2, always)**: #Psytrance #PsychedelicTrance (channel identity)
3. **Dedicated genre (1)**: #[Genre] (e.g. #Dubstep, #DeepHouse, #Synthwave)
4. **Secondary (3)**: #WorshipMusic #MentalHealthAwareness #UNITY
5. **Bank (1-2, rotate for SEO)**: draw from the bank below

### Hashtag Bank (rotate these for keyword/SEO coverage)
```
#StudyMusic #GamingMusic #WorkoutMusic #TrippyVisuals #PsychedelicVisuals
#BassMusic #EDMProducer #PsytranceProducer #MusicProduction #FLStudioEDM
#AbletonLive #DJSet #TrackPreview #Ajja #PsychedelicMusic
#PsytranceWorld #PsytranceCulture #PsytranceArt #PsytranceCommunity
#Zenonesque #HiTechPsytrance #MelodicEDM #ProgressiveTrance #DanceLiveLoveArtLife
#Trance #House #BPM #Creativity #SpiritualEnlightenment #Spirituality
#PsytranceFamily #FullOnPsytrance #ProgressivePsytrance #GoaTrance #DarkPsy
#PsytranceMix #DJMix #NewEDM #HyperNexus
```

### Rules
- Always include #Psytrance in 1-3 hashtags per post
- Always include the dedicated genre hashtag
- All content is EDM with a specific genre style — hashtag both
- `build_hashtags()` in `youtube_update_descriptions.py` auto-generates this

## Content Originality System (2026-08-24)

### Varied Mission Verbiage (NEVER repeat the same text)
`daily_scheduler.py` has `MISSION_VARIATIONS` — 8 different phrasings of the Bob & Lum / Hymnmania story. `build_post()` randomly picks one per post.

### Inquisitive Reel CTAs (5 rotations)
`fb_stories.py` `post_to_facebook_reel()` rotates 5 short question CTAs:
- "Can this [genre] frequency elevate your spirit? 👇"
- "Which hymn should we resurrect next? 👇"
- "Does electronic worship hit different for you too? 👇"
- "Feel that beat sync with your soul? 👇"
- "Would you dance to this in a cathedral of light? 👇"

### Link Spacing (CRITICAL)
YouTube links MUST have a blank line BEFORE and AFTER (else preview card doesn't populate):
```
Watch the full 4K visual journey on YouTube!

https://youtube.com/watch?v=XXX

#hashtags
```

### Facebook Reels Caption Field
Use `keyboard.type()` (NOT `execCommand`) — the field placeholder is "Describe your reel...". React ignores execCommand.

### Facebook Reels — WORKING (FIXED 2026-08-24)
Complete working flow:
1. facebook.com/reels/create
2. Upload 9:16 video (input[type=file])
3. Wait for "Your reel is safe to publish!" (copyright check)
4. Click "Next" (edit options)
5. Click "Next" (caption step)
6. Type caption via keyboard.type (NOT execCommand — React ignores it). Field placeholder = "Describe your reel..."
7. SCROLL DOWN (mouse.wheel 3000) to reveal the Post button
8. Click "Post" by mouse COORDINATES (not JS .click() — the button is below the fold and JS click hits wrong element)
   - Get rect: Array.from(buttons).filter(text==='Post'), scrollIntoView, getBoundingClientRect, mouse.click(cx, cy)

CRITICAL: The Post button is BELOW the fold. MUST scroll + click by coordinates. JS .click() on the hidden button does nothing.

### Facebook Stories — WORKING
`stories/create` → upload 20s 9:16 clip → "Share to story". Confirmed live.

### YouTube Shorts — WORKING
9:16 vertical <60s, `#Shorts` in title, full description with ≤15 hashtags SEO + #EDM + #Psytrance + genre.
