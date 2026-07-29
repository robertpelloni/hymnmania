# HymnMania Roadmap

## Phase 1: MIDI → MP3 Pipeline ✅

- [x] FluidSynth rendering with soundfonts
- [x] Speed variants (0.5x, 1.0x, 1.5x, 2.0x, 3.0x)
- [x] Batch rendering (~33K MIDI files)
- [x] Audio modification (pitch shift, filtering, delay)
- [x] Database: 11,479 hymns with SHA256 dedup, 1,388 with lyrics

## Phase 2: Suno AI Generation ✅

- [x] Audio upload via CDP (Suno API)
- [x] Genre conditioning (11 genres: psytrance, gabba, dubstep, dnb, deep house, detroit techno, detroit house, chiptune, synthwave, japanese hardcore techno, hardstyle trance)
- [x] Clip polling + download (A/B versions)
- [x] Extend / continuation generation
- [x] v5.5 model selection
- [x] **Cover pipeline**: Upload hymn as original track → Create Cover (not vague influence)
- [x] **Classical pipeline**: 104 classical covers across genres
- [x] **Studio Reversal** (v1.37.0): Validated, Packaged & Web-Integrated

## Phase 3: Video Rendering ✅

- [x] MilkDrop visualization via projectM
- [x] FFmpeg video compositing (audio + visualizer)
- [x] Beat-synced video composition with phrase-boundary clip switching
- [x] Magnific AI video clip generation (MiniMax Hailuo 2.3 Fast 768p)
- [x] Quick composer with ffmpeg crossfade + Magnific clips
- [x] 400+ YouTube videos rendered

## Phase 4: Distribution 🔄

- [x] YouTube upload automation (OAuth2)
- [x] YouTube title standardization (Hymn + Classical formats)
- [x] YouTube description templates with social links
- [x] Facebook posting automation (CDP via Edge)
- [x] Facebook post template with video preview cards
- [x] Instagram posting template + credentials
- [x] Single-page Dashboard Console (`dashboard_server.py` at port 8083)
- [x] Background System Tray Server Manager (`systray_app.py`)
- [x] Daily scheduler for automated social posting
- [ ] TikTok integration
- [ ] YouTube playlist management
- [ ] Cross-platform auto-cropping (9:16 for Shorts/Reels/TikTok)

## Phase 5: Future

- [ ] Holiday themed megamixes — mix multiple hymns per genre into one long video
- [ ] All-genre megamix — combine best segments from each genre
- [ ] Multi-voice vocal harmonization (ElevenLabs)
- [ ] Auto-DJ/Live Stream: 24/7 YouTube live stream with real-time MilkDrop
- [ ] Local AI Audio Cover Generation (Stable Audio Open, AudioCraft)
