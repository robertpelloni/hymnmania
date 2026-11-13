# HymnMania Roadmap (v5.97.41)

## Phase 1: MIDI → MP3 Pipeline ✅

- [x] FluidSynth & sine rendering with soundfonts (`scripts/audio_speed_variants_exporter_for_multi_tempo_runs.py`)
- [x] Speed variants (0.5x, 1.0x, 1.5x, 2.0x, 3.0x) + tempo-exact Psytrance sub-genre targeting (`gen_psytrance_tempo.py`)
- [x] Batch rendering (~33K hymn MIDIs + ~29.6K classical MIDIs)
- [x] Database: 11,479 hymns with SHA256 dedup, 1,388 with lyrics
- [x] Curated active hymn pool (`HYMNS_POOL.md`, ~100 hymns) & ACRCloud melody block quarantine (`BLOCKED_HYMNS.md`)

## Phase 2: Suno AI Generation & Mastering ✅ / 🔄

- [x] Dedicated Edge CDP browser on port `9333` (`launch_dedicated_browser.py`, `.dedicated-edge-profile`)
- [x] Live `Authorization: Bearer <jwt>` interception (`suno_auth.py`) replacing retired Clerk JS SDK & rotating `__session` cookies (`v5.97.40`)
- [x] One-upload-many-covers throttled orchestrator (`suno_throttle.py`, `upload_robust2.py`) avoiding pitch-invariant self-match rejections (`v5.97.37`)
- [x] Canonical full-length MediaRecorder blob capture (`cap_cycle.py`) with confirmed seek, `loop_score` validation, mid-song silence scan, and spectral centroid >1200 gate
- [x] Genre EQ post-capture mastering (`master_cover.py` — bass boost + >2kHz harshness taming)
- [x] **1,487 free-credit promo covers banked** across 66 hymns (`.promo_sprint.json`, `.promo_sprint_r2.json`)
- [x] **Submodule `ableton_psytrance_hymn_creator` (`v1.18.5`)**: Algorithmic Psy-Mono + House sequencers, Matchering -7 LUFS mastering, dual `udio_automation.py` / `HeadlessSuno` AI bridge
- [ ] **Suno Studio Cover UI Adaptation**: Trace Suno's post-`v5.97.40` cover trigger inside `Studio` (`Edit in Studio` / `/api/generate` payload) after removal of `Remix -> Cover` from the song menu

## Phase 3: Video Rendering ✅

- [x] MilkDrop visualization via projectM (`1,957` presets)
- [x] Beat-synced full-length video composer (`quick_composer.py`, `compose_pending.py`) using `ffprobe` VBR-accurate durations + Magnific AI clips
- [x] INTRO/OUTRO Impact typography + custom genre/hymn thumbnails (`youtube_thumbnails.py`)
- [x] 60-second 9:16 `1080x1920` Shorts & `<50 MB` (`-crf 28`) compressed social Reels (`post_to_youtube.py`, `scripts/vertical_video_cropper.py`)

## Phase 4: Multi-Platform Distribution & Scheduling ✅

- [x] Unified daily scheduler (`scheduler_v2.py`, `MAX_UPLOADS_PER_DAY = 96`, measured YouTube channel limit ~99–100/day shared by Full + Shorts)
- [x] Windows Scheduled Tasks + failover (`run_scheduler.bat` 3 PM, `run_scheduler_backup.bat` 8 PM `--catchup`, `browser_watchdog.py` + `cleanup_tabs.py` tab pruning on port `9222`)
- [x] YouTube Full + Shorts OAuth2 publisher (`post_to_youtube.py`) with automated quality gate & exact title deduplication
- [x] Verified live social Reels on port `9222`: TikTok (`tt_post.py`), Facebook Reel (`fb_reel_post.py`), Facebook Stories (`fb_stories.py`), Instagram Reel (`ig_cdp_post.py`)
- [x] Zernio + Catbox TikTok batch API pipeline (`scripts/zernio_tiktok_batch.py`, `scripts/zernio_batch_upload.py`, `scripts/zernio_upload.py`)
- [x] Personal cross-platform blog mirror (`social_media_mirror.py` — YouTube, Facebook, Twitter/X, LinkedIn, Bluesky)
- [x] Multi-channel configuration (`youtube_channels.json`: `@ResurrectingBeats` hymns vs `@SymphonicPsychedelic` classical)
- [ ] Dedicated classical channel scheduler (`@SymphonicPsychedelic` using `CLASSICAL_PIECES.md`)
- [ ] YouTube playlist management & Community tab automation (500+ subscriber threshold)

## Phase 5: Future

- [ ] Holiday & all-genre megamixes — long-form continuous mixes per genre
- [ ] Multi-voice vocal harmonization (ElevenLabs / Demucs stems)
- [ ] 24/7 YouTube Live Stream radio with real-time MilkDrop + Icecast (`radio_server.ts`)
- [ ] Local AI Audio Cover Generation fallback (Stable Audio Open / AudioCraft)
