import hymn_player_ext
import os
import numpy as np
import soundfile as sf

def test_export():
    # Setup - need a valid MIDI file and soundfont
    midi_file = 'hymn_remaker/output/verify_psy_default.mid'
    sf_file = 'hymn_remaker/soundfonts/MV30_SC-55.sf2'
    out_wav = 'hymn_remaker/output/export_test.wav'

    if not os.path.exists(midi_file) or not os.path.exists(sf_file):
        print("Skipping real test - dependencies missing.")
        return

    player = hymn_player_ext.HymnPlayer(sf_file)
    player.load(midi_file)

    # Render 2 seconds
    fs = 44100
    frames = fs * 2
    audio = player.render_audio(frames)

    # Reshape to stereo if needed
    audio = audio.reshape(-1, 2)

    sf.write(out_wav, audio, fs)
    print(f"Export Success: {out_wav} created.")

if __name__ == "__main__":
    test_export()
