import aubio
import numpy as np
samplerate = 44100
hop_s = 512
s = aubio.source('hymn_remaker/output/test_vocal/sine_440.wav', samplerate, hop_s)
pitch_o = aubio.pitch("default", 1024, hop_s, samplerate)
while True:
    samples, read = s()
    pitch = pitch_o(samples)[0]
    conf = pitch_o.get_confidence()
    if read < hop_s: break
    if conf > 0.1:
        print(f"Pitch: {pitch}, Conf: {conf}")
