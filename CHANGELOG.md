# Changelog

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
