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
| Artist | `Artist: HYMNMANIA` | `FULL ARTIST: RESURRECTING BEATS / HYMNMANIA` |
| Record Label | `Record Label: RESURRECTING BEATS` | — |
| Genre | `Genre: {genre_name} / Electronic Worship` | `GENRE: {genre} / Electronic Worship` |
| Year | `Year: 2026` | `YEAR: 2026` |

- Use spaces around slashes: `" / "` NOT `"/"`
- On Facebook, use double newlines between categories
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
🎵 Stream/Download [Song Title]: Coming Soon

Connect with Resurrecting Beats:
Stream: Coming Soon
Instagram: Coming Soon
TikTok: Coming Soon

Track Details:

🏷️ Artist: HYMNMANIA
🏢 Record Label: RESURRECTING BEATS
🎼 Track: [Song Title]
🎹 Genre: [Genre] / Electronic Worship
📅 Year: 2026
⚡ Tempo/Variant: [Speed]

About this video:
[2-3 sentences about the visual style]

🙏 Our Mission:
[mission text]

🧠 The Science of Psytrance & Healing:
[science text]

⚙️ How We Make Our Music:
[production text]
```

---

## Facebook Post Template

```
[Headline: 1-2 punchy sentences with emojis]

FULL ARTIST: RESURRECTING BEATS / HYMNMANIA

YEAR: 2026

GENRE: [Genre] / Electronic Worship

Listen and watch the full journey here:
[YouTube Link]

#ResurrectingBeats #Hymnmania #ElectronicWorship [genre hashtags]
```

**CRITICAL**: Double newlines (blank line) between EVERY category for proper rendering. Spaces around slashes.

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
