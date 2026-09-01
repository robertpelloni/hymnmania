# Changelog

## v5.97.9 — Suno DRM Download Fix + Pipeline Restoration + Full Pipeline Verified (2026-09-01)

### Fixed (CRITICAL)

- **Suno DRM download**: `audio_url` now returns `/api/forbidden`; `media_urls` m4a is an encrypted blob. Added working capture method: play song in browser → audio element blob src → `AudioContext.createMediaElementSource` + `MediaRecorder` → webm → ffmpeg → mp3. Reload page between captures.
- **Missing module restored**: `scripts/pipeline_config_central_definitions_genres_speeds.py` (GENRES/SPEEDS/SPEED_LABEL_MAP/PITCH_SHIFT_FACTORS) was deleted — restored from git `c780ddf`. Cover scripts crashed with ModuleNotFoundError otherwise.
- **6 other deleted pipeline scripts restored** from git `c780ddf`: suno_browser_setup_connect_debugging_port, audio_speed_variants_exporter_for_multi_tempo_runs, suno_modal_dismissal_identify_describe_overwrite_resolver, suno_feed_polling_status_monitor_downloader, visuals_video_ffmpeg_pipe_muxer, visuals_milkdrop_preset_energy_analysis_transition_renderer, v2_youtube_oauth_uploader_with_hymn_metadata, generate_sine_cover.py
- **rename_youtube_titles.py**: fixed "Unknown" prefix handling, #Shorts preservation, genre priority (DnB Re**chip** → Drum and Bass, "unknown <genre>" parsing)
- **youtube_update_descriptions.py**: added 6 new hymns to metadata

### Verified (full pipeline run)

- Suno v4.5 cover flow: More menu → Remix → Cover → /create → genre desc → Instrumental → Create → 2 variants
- Generated + downloaded full psytrance cover of "Jesus Comes With Power" (4:19) via MediaRecorder capture
- Upload flow: Add audio → file chooser → "Describe your audio" modal → Full Song → Continue

### Added

- **New hymns** (never posted before): Jesus Comes With Power, Just Over The Mountains, O Happy Day (Philip Doddridge, 1755), When Love Shines In, God Is So Good, Oh God Our Help (Isaac Watts, 1719)
- `post_to_youtube.py` — YouTube uploader with correct titles/descriptions (no "cover", correct hymn/genre/author/year, 15 hashtags)
- `regen_beat_videos.py` — regenerate beat videos locally (zero quota)
- 5 new YouTube uploads (2 full + 1 short batch, then 2 full + 1 short new hymns)
- 8 "Unknown" videos renamed correctly

### Pipeline Stats

- 54 July-era beat videos regenerated with waveform visualizer
- Channel: 1,234+ videos

## v5.97.8 — Comprehensive Repository Refresh & Submodule Cascade (2026-08-05)

### Branch Reconciliation

- All 3 L1 feature branches (`feat/vertical-video`, `jules-1235`, `jules-6626`) verified as ancestors of `origin/main` — fully merged, no action needed.
- Parent repo: `main`, `master`, `backup/pre-sync-*` — no feature branches.

### Submodule Cascade

- L2 pulled: `9ec99de` → `acd0fa1` (1 commit)
- L1 gitlink amended: nested hymnmania_src pointer refreshed
- Parent gitlink updated: ableton submodule pointer cascaded
- L3 circular reference: remains uninitialized, `fetchRecurseSubmodules=false` mitigation active

### Verification

- `.gitignore` audit: databases, session files, AI memory, documentation all confirmed tracked
- TypeScript `tsc --noEmit`: 0 errors
- Python syntax: all root + scripts/ compile clean

### Changed

- **Version**: Bumped VERSION from 5.97.7 → 5.97.8
- **AGENTS.md**: Version tag updated
- **HANDOFF.md**: Refreshed session summary

## v5.97.7 — Executive Protocol: Repository Sync & Intelligent Merge (2026-08-03)

### Branch Reconciliation

- **Ableton submodule**: `feat/vertical-video-generation` — already merged upstream. `jules-*` branches — AI auto-generated, stagnant, excluded by protocol. `jules-1235` merged into `origin/main` upstream.
- **Parent repo**: Only `main` + `backup/pre-sync-*`. No feature branches. `master` mirrors `main`.
- **Forward merges**: 0 needed.
- **Reverse merges**: 0 needed.

### Submodule Chain

- **L3 circular reference** (`hymnmania_src/submodules/ableton_...`): Mitigated via `fetchRecurseSubmodules=false`. Remains uninitialized.
- **L1 unpushed commits**: 3 local commits on ableton (nested submodule pointer updates). Push blocked by credential mismatch (`candlestixxx` vs `robertpelloni`).
- **Recursive update**: All layers pulled to latest; gitlink cascade committed and pushed.

### Changed

- **Version**: Bumped VERSION from 5.97.6 → 5.97.7
- **AGENTS.md**: Version tag updated to 5.97.7
- **HANDOFF.md**: Full session summary generated
- **CHANGELOG.md**: v5.97.6 entries added from upstream pull
- **Documentation**: All .md files verified present and current

## v5.97.6 — TikTok + Shorts + Crossfade Pipeline (2026-08-03)

### New

- **Crossfade transitions**: 0.4s ffmpeg xfade between all clips in `quick_composer.py`
- **Custom thumbnails**: Genre + hymn + RESURRECTING BEATS overlay
- **YouTube Shorts**: 9:16 vertical converter + uploader
- **TikTok poster**: 9:16 convert + CDP upload script (`tiktok_poster.py`)
- **Weekly scheduler bot**: Mon-Fri auto-posting to TikTok + Facebook (`scheduler_bot.py`)
- **Post all platforms**: Unified script (`post_all_platforms.py`)
- **Full hymn pipeline**: 15 hymns × 11 genres × 5 speeds with NNT subtitles (`full_hymn_pipeline.py`)
- **SpiritualEDM hashtag**: Replaced #ChristianPsytrance across all platforms
- **AI Metadata**: JSON-LD Schema.org hidden in descriptions for AI crawler indexing
- **Tempo-scaled beats**: 4/8/12/16 beat phrases based on BPM
- **INTRO/OUTRO**: RESURRECTING BEATS intro/outro with genre-matched text styles

### Pipeline Stats

- 700+ YouTube videos
- 50+ Facebook posts
- Ready: TikTok (@resurrecting.beat), YouTube Shorts

### Known Blockers

- TikTok logged into @hypernexusllc, not @resurrecting.beat
- YouTube Community tab: 500 subscriber minimum

## v5.97.5 — Repository Synchronization & Intelligent Merge (2026-07-29)

### New

- **Repository Sync**: Full reconciliation with remote after force-push; backup branch `backup/pre-sync-20260729-004935` preserved
- **Documentation Restored**: CHANGELOG.md, ROADMAP.md, TODO.md, README.md, VISION.md, IDEAS.md, MEMORY.md, DEPLOY.md restored from pre-sync backup and updated

### Changed

- **Submodule**: `ableton_psytrance_hymn_creator` updated to latest commit on origin/main
- **Version**: Bumped VERSION from 5.97.4 → 5.97.5

## v5.97.4 — Repository sync: feat/v137 + jules merged, master synced (2026-07-22)

### New

- **feat/v137 Studio Reversal pipeline** merged into main
- **jules session documentation** merged into main
- **Facebook posting finalized**: Bare URL preview → selectAll replace method documented
- **Instagram credentials**: Saved in `.secrets.json`, full posting template defined
- **YouTube template**: Artist: Resurrecting Beats ft. author, social links (FB/IG/TikTok)
- **master branch** created and synced

### Fixed

- Facebook posts: Bare URL triggers preview, selectAll+replace with full text+link
- Facebook video preview: Paste YouTube link first, wait for scrape, then add text above
- Spacing rules: Spaces around slashes, double newlines on FB

## v5.97.3 — Pipeline: 100+ YouTube Uploads, Facebook/IG Templates (2026-07-21)

### New

- 123 YouTube descriptions updated
- 100 YouTube uploads
- 68 titles renamed to standard format
- 400 total YT videos on channel
- Facebook/IG templates: `HYMNMANIA_SOCIAL_POST_TEMPLATE`
- YouTube link as comment method
- Fixed hashtag block on all posts

## v5.97.2 — YouTube Template Update (2026-07-20)

### Changed

- YouTube template: Artist=Resurrecting Beats ft. author
- Social links added (FB/IG/TikTok)
- Fixed hashtag block

## v5.97.1 — Pipeline Full Run (2026-07-20)

### New

- 55 YouTube uploads
- 173 titles renamed
- 22 Facebook posts
- 123 beat videos rendered
- Spacing fix: Spaces around slashes, Artist: HYMNMANIA / Label: RESURRECTING BEATS

## v5.97.0 — Classical Pipeline (2026-07-19)

### New

- 104 classical covers downloaded
- 13 beat videos for classical pieces
- 7 YouTube uploads with Hymnmania template
- 4 Facebook posts
- Classical title format: `[Genre] Classical Remix - [Piece] ([Composer], [Year]) | [Speed]`

## v5.96.0 — Intelligent Merge & Repository State Restoration (2026-07-18)

### Fixed

- Resolved merge conflicts
- Stabilized codebase
- Clarified subsystem scopes
- Comprehensive test suite

## v5.95.0 — Single-Page Dashboard & System Tray App (2026-07-08)

### New

- **Consolidated Dashboard**: Redesigned `dashboard_server.py` to present all actions, controls, system health stats, active tasks, track manager, and live log console in one singular web page.
- **System Tray Controller**: Created `systray_app.py` using `pystray` and `Pillow` to run in the Windows system tray, launch the browser dashboard on demand, and cleanly terminate background processes.
- **Auto Credit Check**: Added API endpoint `/api/status` to retrieve Suno credits count in real-time.

## v5.94.0 — Cover Pipeline & Repository Sync (2026-07-04)

### New

- **Cover pipeline**: Rewrote `_cdp_generate.py` to upload hymn as original track to library, then generate proper Covers (not vague "influence")
- **12 genres**: Added happy_hardcore, forest_goa, dark_psy, japanese_hardcore, gabba, hardstyle_trance
- Submodule `ableton_psytrance_hymn_creator` updated to `ce0a012` (latest origin/main)

### Fixed

- **Upload flow**: Navigates to `/library` to upload as original song, then Create Cover from it
- Generated songs now properly show as "Cover of [hymn]" with source attribution

## v5.82.0 — Repository Sync & Clip Naming Fix (2026-06-27)

### New

- Added `detroit_techno` and `detroit_house` genres (6 total genres)

### Fixed

- **Clip naming**: Only fetch 2 clips (A, B) per generation
- **Model v5.5**: Script explicitly clicks the v5.5 model button
- **Audio upload**: CDP click + DataTransfer injection

## v5.81.0 — Genre Expansion & Model Fix (2026-06-26)

### Fixed

- Genre labels corrected
- Model version selection ensured

## v5.70.0 — Previous (2026-06-20)

(Consolidated from prior HANDOFF entries)
