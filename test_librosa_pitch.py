import librosa
import numpy as np
import mido

def transcribe(audio_path, midi_path):
    y, sr = librosa.load(audio_path)
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Simple conversion
    times = librosa.times_like(f0)
    last_midi = None

    for val, t in zip(f0, times):
        if np.isnan(val):
            if last_midi is not None:
                track.append(mido.Message('note_off', note=last_midi, velocity=0, time=100))
                last_midi = None
            continue

        midi_note = int(round(librosa.hz_to_midi(val)))
        if midi_note != last_midi:
            if last_midi is not None:
                track.append(mido.Message('note_off', note=last_midi, velocity=0, time=100))
            track.append(mido.Message('note_on', note=midi_note, velocity=100, time=0))
            last_midi = midi_note

    mid.save(midi_path)
    print(f"Saved {midi_path}")

transcribe('hymn_remaker/output/test_vocal/sine_440.wav', 'hymn_remaker/output/test_vocal/librosa_transcribed.mid')
