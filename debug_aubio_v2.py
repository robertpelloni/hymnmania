import aubio
import numpy as np
samplerate = 0 # use native
hop_s = 512
s = aubio.source('hymn_remaker/output/test_vocal/sine_440.wav', samplerate, hop_s)
samplerate = s.samplerate
pitch_o = aubio.pitch("default", 2048, hop_s, samplerate)
count = 0
while True:
    samples, read = s()
    pitch = pitch_o(samples)[0]
    conf = pitch_o.get_confidence()
    if conf > 0.1:
        print(f"Pitch: {pitch}, Conf: {conf}")
    count += 1
    if read < hop_s or count > 100: break
