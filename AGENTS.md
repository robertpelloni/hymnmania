# HymnMania — Agent Instructions

> **Version: 5.97.1**
> **Last updated: 2026-07-22**
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

```
{{HOOK_TEXT}} 🚀

🎵 Track: {{SONG_TITLE}}
🎹 Vibe: {{GENRE_OR_VIBE}}
📺 Watch the full visual journey on YouTube! {{LINK_CTA_TEXT}}

{{VISUAL_EXPERIENCE_SUMMARY}} Our visuals are crafted by our creators using multiple digital media tools to deliver the ultimate psychedelic experience.

Every track is meticulously produced using Hymnmania, a custom software automation tool engineered by Bob & Lum to fuse faith, code, and electronic music. We believe psytrance is more than music — its fast, repetitive tempos stimulate the brain's reward pathways and induce a state of deep meditation and stress relief. 🙏🧠

Head over to the Resurrecting Beats YouTube channel to stream it now! Let us know in the comments how this frequency makes you feel. 👇

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#ResurrectingBeats #Hymnmania #ChristianPsytrance #Psytrance #ElectronicMusic #WorshipMusic #MusicTherapy #MentalHealthAwareness
```

### Facebook Posting Rules

1. Post the generated text to the Resurrecting Beats Facebook Page
2. Set `{{LINK_CTA_TEXT}}` to: `(Full 4K visual journey on YouTube - link in top comment! 🔗)`
3. After posting, add a follow-up comment with the direct YouTube link: `{{YOUTUBE_VIDEO_URL}}`
4. Upload the MP4 video file directly if possible (native video upload), otherwise post text + link
5. **CRITICAL**: Use the exact fixed hashtag block — no dynamic genre hashtags

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

| Step | Script |
|------|--------|
| YouTube Descriptions | `youtube_update_descriptions.py` |
| YouTube Title Rename | `rename_youtube_titles.py` |
| Facebook Poster | `daily_scheduler.py` |

## Credentials

- **YouTube**: `token.json` (OAuth refreshable)
- **Facebook**: via Edge CDP browser (port 9222, profile `edge-cdp-profile`)
- **Magnific**: `~/.env` (needs credits)
- **Channel**: Resurrecting Beats (@ResurrectingBeats)
