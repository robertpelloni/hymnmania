# Handoff - Version 1.28.0 (Vocal Remix & Udio Extension Hack)

## Session Summary
Building upon the Psy-Mono foundation, this session implemented the automated Vocal Remix pipeline for integrating hip-hop acapellas and the Udio "Extension Hack" for improved stylistic transformations.

## Major Changes
- **Vocal Remix Pipeline (TS):**
  - `src/integrators/vocal_processor.ts`: Full implementation with Demucs isolation, librosa BPM analysis, and FFmpeg grid-locking.
  - `main.py`: Added `--mix-vocals` argument to orchestrate hip-hop vocal integration.
  - `app.py`: Added UI input for "Hip-Hop Vocal Remix".
- **Udio Power User Hack:**
  - `udio_remaker.py`: Implemented the 15-second crop and 'extend' mode logic to bypass soundfont texture bleed and force 100% electronic instrumentation.
- **Robustness:**
  - Standardized `ts-node` calls with `--transpile-only` to avoid environment-specific type checking issues in production execution.
  - Fixed `cookie_string` compat issue in `UdioRemaker`.

## Environment Updates
- New Python dependency: `librosa`.
- New Node.js dependency: `@types/node` (dev).

## Verification Status
- TS Sequencer and VocalProcessor verified to load and execute via `ts-node`.
- `main.py` verified to parse new arguments and correctly branch for Psytrance and Vocal Remix modes.
- `app.py` verified to display and pass new experimental parameters.

## Outstanding Items / Next Steps
- Implement `yt-dlp` download logic in `main.py` for direct YouTube URL vocal mixing.
- Full end-to-end integration test with a live GPU for Demucs separation.
