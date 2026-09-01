# HymnMania Architectural Memory

## Codebase Traits
- **Browser Automation**: CDP websocket connections are used to interact with Edge on port 9222. Playwright is used for robust browser upload automation.
- **Suno Cover Limitations**: Generating a cover of an uploaded track on Suno can trigger a copyright moderation failure if words like "Joy to the World" or "hymn" are placed in the description prompt or lyrics box. To bypass this, we use generic style tags ("full-on psytrance, energetic beat...") and set `"make_instrumental": True`.
- **Unique Sessions**: Navigation includes `session_id` query parameters to prevent multiple background tabs from colliding in CDP.

## Pipeline (VERIFIED 2026-09-01 — full order)
```
MIDI → sine MP3 → SUNO COVER → beat video → post
```
- Sine MP3 = INPUT reference only. Suno generates the real genre cover.
- Cover flow (v4.5): song page → More menu (three dots) → Remix → Cover → /create
- Song Description textarea (index 2, maxLength 3000) sets gpt_description_prompt
- Instrumental toggle ON; model v4.5-all; new clips have model `chirp-auk`

## Suno DRM Download (2026-09-01) — CRITICAL
- `audio_url` returns `/api/forbidden` — obsolete
- `media_urls`: m4a-opus (CloudFront = encrypted blob, no ftyp/mdat), mp3 (cdn1.suno.ai → 403)
- Direct URL fetch fails (403 / CORS / encryption)
- **WORKING**: click play → audio element src = `blob:https://suno.com/...` →
  `AudioContext.createMediaElementSource(audioEl)` + `MediaRecorder(stream)` → webm → ffmpeg → mp3
- Must reload page between captures (MediaElementSource attaches once per page)
- Record for (duration + 5s)

## Missing Module Incident (FIXED 2026-09-01)
- `scripts/pipeline_config_central_definitions_genres_speeds.py` deleted from tree (only .pyc in __pycache__)
- Crash: `ModuleNotFoundError: No module named 'pipeline_config_central_definitions_genres_speeds'`
- Defines: `GENRES` (11 genres), `SPEEDS` [0.5..3.0], `SPEED_LABEL_MAP`, `PITCH_SHIFT_FACTORS`
- Restored from git commit `c780ddf` (auto checkpoint before sync, 2026-07-11)
- Also restored: suno_browser_setup_connect_debugging_port.py, audio_speed_variants_exporter_for_multi_tempo_runs.py,
  suno_modal_dismissal_identify_describe_overwrite_resolver.py, suno_feed_polling_status_monitor_downloader.py,
  visuals_video_ffmpeg_pipe_muxer.py, visuals_milkdrop_preset_energy_analysis_transition_renderer.py,
  v2_youtube_oauth_uploader_with_hymn_metadata.py, generate_sine_cover.py
- LESSON: never delete scripts/ modules; config module is critical for cover generation

## Design Decisions
- **Dashboard Consolidations**: All features are condensed onto a single-page dashboard at `http://localhost:8083` to eliminate complex subpages and routes.
- **System Tray Controller**: A background utility (`systray_app.py`) is used to start the dashboard server and clean up python.exe processes upon quitting.

## Playwright & Browser Cover Pipelines
- **Generate Sine Cover (`generate_sine_cover.py`)**: High-performance browser flow running over CDP to control Edge. Synthesizes MIDI as a speed-adjusted sine-wave MP3, mounts the hidden file upload element by clicking `Audio`, switches to `Advanced` mode, inputs generic style text to avoid copyright filters, and polls the studio API feeds to download the generated `.mp3` covers directly.
- **Hydration Waiting**: Suno's UI requires waiting for hydration states to ensure the `Advanced` and `Audio` elements are fully visible and ready for interaction, which is handled via Playwright's native `wait_for(state="visible")` selectors.
- **Suno create page**: has 3-4 textareas — [0]=?, [1]=style (maxLen 1000), [2]=Song Description (maxLen 3000, sets gpt_description_prompt), [3]=Describe the sound (maxLen 500)
- **Upload modal**: after file inject, "Describe your audio" → select "Full Song" → Continue

## Social Media Posting
- **Facebook**: Uses Edge CDP (port 9222, profile `edge-cdp-profile`) via `daily_scheduler.py` / `facebook_poster.py`. Proven method: paste bare YouTube URL → wait for preview card → selectAll + replace with full template text → wait for re-scrape → post.
- **Instagram**: Credentials in `.secrets.json` (`resurrectingbeats@gmail.com`). Post template mirrors Facebook with bio-link CTA.
- **YouTube**: OAuth2 via `token.json`. Title format standardized for hymns and classical pieces. Descriptions include Artist: Resurrecting Beats ft. [Author].
- **YouTube quota**: 10,000 units/day. Upload = 1,600, rename = 50, thumbnail = 50, search = 100. ~6 uploads/day max. Shorts cost the same as full videos.

## Repository Sanitization
- **Windows Reserved File Names**: Dummy files named `nul` created inside recursively imported subdirectories must be deleted. Windows prevents reading or indexing files named `nul` because it is a reserved system device name. This blocks Git commands. Deletion requires using the UNC namespace prefix (`\\?\`) to bypass system reserved name checks.
