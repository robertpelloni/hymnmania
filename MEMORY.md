# HymnMania Architectural Memory

## Codebase Traits
- **Browser Automation**: CDP websocket connections are used to interact with Edge on port 9222. Playwright is used for robust browser upload automation.
- **Suno Cover Limitations**: Generating a cover of an uploaded track on Suno can trigger a copyright moderation failure if words like "Joy to the World" or "hymn" are placed in the description prompt or lyrics box. To bypass this, we use generic style tags ("full-on psytrance, energetic beat...") and set `"make_instrumental": True`.
- **Unique Sessions**: Navigation includes `session_id` query parameters to prevent multiple background tabs from colliding in CDP.

## Design Decisions
- **Dashboard Consolidations**: All features are condensed onto a single-page dashboard at `http://localhost:8083` to eliminate complex subpages and routes.
- **System Tray Controller**: A background utility (`systray_app.py`) is used to start the dashboard server and clean up python.exe processes upon quitting.

## Playwright & Browser Cover Pipelines
- **Generate Sine Cover (`generate_sine_cover.py`)**: High-performance browser flow running over CDP to control Edge. Synthesizes MIDI as a speed-adjusted sine-wave MP3, mounts the hidden file upload element by clicking `Audio`, switches to `Advanced` mode, inputs generic style text to avoid copyright filters, and polls the studio API feeds to download the generated `.mp3` covers directly.
- **Hydration Waiting**: Suno's UI requires waiting for hydration states to ensure the `Advanced` and `Audio` elements are fully visible and ready for interaction, which is handled via Playwright's native `wait_for(state="visible")` selectors.

## Social Media Posting
- **Facebook**: Uses Edge CDP (port 9222, profile `edge-cdp-profile`) via `daily_scheduler.py` / `facebook_poster.py`. Proven method: paste bare YouTube URL → wait for preview card → selectAll + replace with full template text → wait for re-scrape → post.
- **Instagram**: Credentials in `.secrets.json` (`resurrectingbeats@gmail.com`). Post template mirrors Facebook with bio-link CTA.
- **YouTube**: OAuth2 via `token.json`. Title format standardized for hymns and classical pieces. Descriptions include Artist: Resurrecting Beats ft. [Author].

## Repository Sanitization
- **Windows Reserved File Names**: Dummy files named `nul` created inside recursively imported subdirectories must be deleted. Windows prevents reading or indexing files named `nul` because it is a reserved system device name. This blocks Git commands. Deletion requires using the UNC namespace prefix (`\\?\`) to bypass system reserved name checks.
