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
| Beat Video Composer | `quick_composer.py` | ffmpeg crossfade + Magnific clips + intro/outro |

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

### Intro/Outro
- **Intro (2.5s)**: "RESURRECTING BEATS" + genre name over random Magnific clip with genre-matched colors
- **Outro (3s)**: "RESURRECTING BEATS" + "Subscribe for more!" with fade-out

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

- **Channel**: @resurrecting.beat
- **URL**: https://www.tiktok.com/@resurrecting.beat?_r=1&_t=ZP-98NBjRbePx0
- **Video format**: Vertical 9:16 (1080x1920) for TikTok/Reels
- **Posting**: To be automated via CDP browser (tikok.com/upload)
- **Template**: (awaiting verbiage — to be documented)

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
- 5-10 YouTube uploads per quota window
- 2-3 Facebook posts per day (staggered genres)
- 1 TikTok/Short per day from best segments
- Rotate featured playlists weekly

### Subscriber Hooks
- **First 3s**: RESURRECTING BEATS intro flash
- **Last 20s**: End screen with subscribe CTA
- **Description**: Clear call-to-action to subscribe
- **Cross-promote**: Link Facebook + TikTok in every description
