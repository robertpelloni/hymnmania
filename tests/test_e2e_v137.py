import pytest
import os
import sys

# Ensure parent directory is in path for imports
sys.path.append(os.getcwd())

from pipeline.processing.sonic_vacuum import SonicVacuumProcessor
from pipeline.processing.symbolic_norm import SymbolicNormalizer
from pipeline.processing.house_quantizer import HouseStructuralQuantizer

def test_pipeline_e2e_v137():
    """Verify all v1.37.0 modules work together."""
    test_input = "test_input_single/short_hymn.mid"
    if not os.path.exists(test_input):
        import mido
        os.makedirs("test_input_single", exist_ok=True)
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.Message('note_on', note=60, velocity=100, time=0))
        track.append(mido.Message('note_off', note=60, velocity=0, time=480))
        mid.save(test_input)

    output_dir = "output_test_batch"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Norm
    norm_path = os.path.join(output_dir, "e2e_norm.mid")
    SymbolicNormalizer(test_input).normalize(norm_path)
    assert os.path.exists(norm_path)

    # 2. House
    house_path = os.path.join(output_dir, "e2e_house.mid")
    HouseStructuralQuantizer(norm_path).quantize(house_path)
    assert os.path.exists(house_path)

    # 3. Vacuum (Speed 2.0)
    vacuum = SonicVacuumProcessor(house_path)
    audio_path = os.path.join(output_dir, "e2e_dry_2x.wav")
    audio, sr = vacuum.render_dry_piano(None, return_audio=True)
    import numpy as np
    audio_20 = audio[::2]
    import scipy.io.wavfile as wavfile
    wavfile.write(audio_path, sr, (audio_20 * 32767).astype(np.int16))
    assert os.path.exists(audio_path)
