# Project Memory & Architectural Observations

- **Hybrid Architecture:** The project has evolved from a pure Python pipeline to a hybrid TypeScript/Python system. TypeScript handles the symbolic music logic (MIDI parsing, algorithmic generation) due to the robust ecosystem (Tone.js).
- **Psy-Mono Pipeline:** This is the core algorithmic psytrance engine. It focuses on extracting melodic intervals from hymns and mapping them to a high-velocity 145 BPM grid.
- **Neural Synthesis:** We use Udio/Suno as "texture mappers." To ensure high-quality output, we render "transient-only" MIDI files (dry, staccato sines) for AI conditioning.
- **Udio Tuning:** Optimal parameters for hymn-based remixes in Udio are: `audio_influence=0.35`, `prompt_strength=0.65`, and `manual_mode=True`.
- **FFmpeg for Audio-Visuals:** FFmpeg remains the backbone for final assembly. Complex filters are used for audio-reactive visualizers and burned-in subtitles.
- **Native C++ Engine:** The `HymnPlayer` engine (pybind11 wrapper around FluidSynth) provides fast, thread-safe rendering for the initial MIDI preview and conditioning stems.
