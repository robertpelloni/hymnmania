# TODO

### v1.37.0 - The Studio Reversal
- [ ] Implement `export_speed_variants` in `SonicVacuumProcessor` (0.5x, 1x, 2x).
- [ ] Update `SunoBrowserAutomation` to loop through speed variants and genre tags.
- [ ] Create `hymn_remaker/src/psy_mono_bridge.py` for the Ableton reversal pipeline.
- [ ] Integrate `demucs` and `basic-pitch` for audio-to-MIDI in the bridge.
- [ ] Add Ableton assembly logic via OSC (`pylive`).

### Immediate Fixes
- [x] Implement LALAL.AI REST API integration as a fall-back for local Demucs.
- [x] Optimize Local MusicGen latency by implementing a quantized model (INT8/FP16).
- [x] Add more complex Markov-chain transition rules to the arpeggiator for "peak climax" variations.

### Enhancements
- [ ] Multi-voice vocal harmonization for hip-hop acapellas using ElevenLabs.
- [ ] Automated video generation matching the 145 BPM grid with audio-reactive visuals.
- [ ] Real-time "Jam Mode" where the sequencer responds to live MIDI controller input.
