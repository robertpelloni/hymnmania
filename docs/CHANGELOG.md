# Changelog

## [1.30.0] - 2026-05-22
### Added
- **Python-Native Psy-Sequencer:** Ported the algorithmic psytrance generation logic from TypeScript to Python (`hymn_remaker/src/psy_sequencer.py`), enabling low-latency integration with the Streamlit UI and removing Node.js overhead for the core pipeline.
- **Enhanced C++ Audio Engine:** Added real-time `set_gain()` and `set_channel_volume()` bindings to the `hymn_player_ext` FluidSynth wrapper, enabling dynamic mixing during playback.
- **Vocal Grid-Locking & Harmonics:** Implemented a dedicated `VocalRemixPipeline` in Python (`hymn_remaker/src/vocal_remix.py`) with automated time-stretching (ratio-based alignment to 145 BPM) and pitch-shifting to match the detected hymn root key.
- **Live Studio V3:**
    - Integrated a **Plotly Piano Roll** visualizer for real-time pattern inspection.
    - Added a **Multi-Channel Mixer** in the UI to control individual volume levels for Kick, Bass, and Lead tracks via the upgraded C++ engine.
- **Unified Versioning:** Centralized version control to `VERSION` and mirrored in `hymn_remaker/VERSION.md`.

### Changed
- **Architecture Shift:** Migrated core symbolic music generation from TypeScript to Python for tighter integration with the ML ecosystem (`librosa`, `torch`).
- **Streamlit Optimization:** Replaced legacy subprocess calls to `ts-node` with direct Python imports, drastically improving UI responsiveness.
- **Merge & Sync:** Reconciled upstream changes and consolidated the codebase across hybrid Python/C++ boundaries.

## [1.28.0] - 2026-05-21
### Added
- **Live Psy-Mono Studio:** Interactive Streamlit tab for real-time algorithmic psytrance parameter tweaking.
- **Real-time Audio Input (pYIN):** Microphone recording and monophonic melody transcription using librosa's pYIN algorithm.
- **Native C++ Real-time Bindings:** Upgraded `HymnPlayer` engine with `fluid_audio_driver` for low-latency system audio output.
- **Local Generative AI:** Integrated `facebook/musicgen-melody` via HuggingFace Transformers for offline, on-device audio rendering.
- **YouTube Audio Extraction:** Native `yt-dlp` integration for pulling hip-hop vocals directly from URL into the remix pipeline.
- **High-Fidelity Export:** Offline WAV rendering module for exporting studio sessions with 44.1kHz stereo quality.

### Changed
- **Security Hardening:** Refactored all CLI-based integrations (FFmpeg, Demucs, yt-dlp) to use argument arrays, mitigating shell injection vulnerabilities.
- **Pipeline Orchestration:** Optimized `main.ts` with `--transpile-only` and better error handling for seamless cross-language execution.

## [1.27.0] - 2026-05-20
### Added
- **Algorithmic Psytrance Pipeline (Psy-Mono):** Initial implementation of a symbolic music generation engine in TypeScript.
- **Hymn DNA Extraction:** Logic to extract chord roots and melodic patterns from MIDI/MusicXML hymns.
- **Procedural Psytrance Generation:** Algorithmic rolling basslines (K-B-B-B) and Euclidean arpeggio gating.
- **Vocal Remix Pipeline:** Automated isolation, time-stretching, and pitch-shifting of hip-hop vocals for psytrance integration.
- **TypeScript/Node.js Environment:** Added a TypeScript-based symbolic processing layer to the project.

### Changed
- Shifted project philosophy from "black box" AI audio generation to hybrid symbolic-algorithmic composition + neural texture mapping.
- Updated documentation across the entire project to reflect the new Psy-Mono architecture.
