# Handoff - Version 1.32.0 (Studio V5 & Library Management)

## Session Summary
Completed the "Live Jam" evolution of the Hymnmania pipeline. Studio V5 now supports real-time FX triggers, text-to-audio novel generation, and a comprehensive library management system with automated quality scoring. The C++ engine has been tuned for high polyphony, and the UI is fully synchronized for multi-track mixing and live performance.

## Major Changes
- **Studio V5: Live Jam Edition:**
    - Real-time manual triggers for Acid Fills, Rising Sweeps, and Crash Cymbals via MIDI CC/Note events in the C++ engine.
    - Integrated "Novel AI" mode for pure text-to-psytrance generation using local MusicGen.
- **Library & Quality Evaluator:**
    - `hymn_remaker/src/quality_evaluator.py`: Automated 0-100 scoring based on spectral/rhythmic features.
    - Persistent library UI with "Load Studio" and deletion capabilities.
- **Optimized Local ML:**
    - MusicGen now runs in FP16 with IPEX/CUDA optimizations, supporting faster iterations.
- **Frontend Verification:**
    - Established a Playwright-based verification suite for UI regression testing.

# Handoff - Version 1.30.0 (Python-Native Psy-Mono Studio & Mixer)

## Session Summary
Successfully transitioned the core "Psy-Mono" pipeline to a high-performance Python-native implementation, eliminating Node.js overhead for the real-time studio. Upgraded the C++ audio engine with multi-channel volume control and implemented a sophisticated vocal alignment pipeline for hip-hop remixes.

## Major Changes
- **Python-Native Psy-Sequencer:**
    - `hymn_remaker/src/psy_sequencer.py`: Ported TypeScript logic to Python using `mido`. Supports instant pattern generation for Kick, Rolling Bass (3 variants), and Euclidean Arpeggios.
- **Enhanced C++ Engine (`hymn_player_ext`):**
    - Added `set_gain(float)` and `set_channel_volume(int, float)` bindings.
    - Enables real-time mixing of separate tracks directly from the Streamlit UI.
- **Vocal Remix Pipeline:**
    - `hymn_remaker/src/vocal_remix.py`: Uses `yt-dlp` for downloads, `Demucs` for isolation, and `librosa` for grid-locking.
    - **Grid-Locking:** Automated calculation of time-stretch ratios to snap vocals to 145 BPM.
    - **Harmonic Alignment:** Automated pitch-shifting of vocals to match the detected hymn root key.
- **Live Studio V3:**
    - `hymn_remaker/app.py`: Integrated **Plotly Piano Roll** for visual feedback.
    - Interactive Mixer: Real-time volume sliders for Kick, Bass, and Lead tracks.
- **Unified Versioning:**
    - Centrally managed version `1.30.0` in root `VERSION` and `hymn_remaker/VERSION.md`.

## Environment Updates
- **Python:** Added `mido`, `plotly`.
- **C++:** Recompiled `hymn_player_ext.so` with new Mixer API.

## Verification Status
- Verified Python sequencer MIDI output via `verify_midi.py`.
- Verified C++ Mixer bindings via `verify_bindings.py`.
- Verified `main.py` integration with the new Python pipeline.
- Verified file presence and version consistency across the repo.

## Outstanding Items / Next Steps
- Implement LALAL.AI REST API as a fallback for cloud-based stem isolation.
- Optimize local AI model weights to INT8/FP16 for reduced latency.
- Integrate a VST3 host into the C++ engine for high-end local instrument rendering.
