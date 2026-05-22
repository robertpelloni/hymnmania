# Handoff - Version 1.27.0 (Algorithmic Psytrance & Preprocessing)

## Session Summary
This session successfully transitioned the project into a hybrid TypeScript/Python architecture to support the "Psy-Mono" pipeline—an expert system for algorithmic psytrance generation inspired by traditional hymns. Additionally, three experimental Python-based preprocessing modules were added to optimize audio for AI LAMs (Udio/Suno).

## Major Changes
- **TypeScript Layer:**
  - `src/analysis/midi_parser.ts`: Extracts "Hymn DNA" (melody and harmony intervals).
  - `src/sequencer/psy_generator.ts`: Generates 145 BPM Full-On Psytrance MIDI patterns with rolling basslines and Euclidean arpeggio gating.
  - `src/main.ts`: CLI bridge for the Python orchestrator to call the TS sequencer.
- **Python Preprocessing Pipeline:**
  - `pipeline/processing/sonic_vacuum.py`: Textureless rendering (sine/dry piano) to prevent AI "soundfont bleed."
  - `pipeline/processing/symbolic_norm.py`: Velocity flattening and performance purging for symbolic AI.
  - `pipeline/processing/house_quantizer.py`: Algorithmic house skeletal framework generation (124 BPM grid snapping).
- **Orchestration & UI:**
  - `hymn_remaker/main.py`: Integrated new preprocessors and the Psytrance TS sequencer.
  - `hymn_remaker/app.py`: Exposed all new experimental features to the Streamlit sidebar.
  - `hymn_remaker/src/udio_remaker.py` & `udio_oauth_remaker.py`: Updated with advanced control sliders (variance, prompt strength, manual mode).

## Environment Updates
- Added `package.json` and `tsconfig.json`.
- Required Node.js dependencies: `typescript`, `@tonejs/midi`, `ts-node`, `axios`.
- Updated `.gitignore` to include `node_modules` and `package-lock.json`.

## Verification Status
- Python tests: `tests/test_pipeline.py` passed (Sonic Vacuum, Symbolic Norm, House Quantizer).
- TypeScript: `npx ts-node src/main.ts` verified to generate valid MIDI from hymn inputs.
- Native Engine: `MidiRenderer` updated and tested with `transient_only` flag.

## Outstanding Items / Next Steps
- Implement `src/integrators/vocal_processor.ts` fully (currently has structure but relies on Python fallback).
- Add specific `transient.sf2` soundfont for Module 1's "dry piano" rendering if high-fidelity staccato is needed.
- Shrink Docker image in Phase 6 as per ROADMAP.
