import os
import logging
from hymn_remaker.src.local_remaker import LocalMusicRemaker

logging.basicConfig(level=logging.INFO)

def test():
    # Use the sine wave as melody conditioning
    melody = 'hymn_remaker/output/test_vocal/sine_440.wav'
    output = 'hymn_remaker/output/test_vocal/local_gen_test.wav'

    remaker = LocalMusicRemaker()
    # Generate a short 2-second snippet for speed
    remaker.generate(melody, "Fast Full-On Psytrance, 145 BPM, electronic", duration=2, output_path=output)

    if os.path.exists(output):
        print(f"Success: {output} created.")
        size = os.path.getsize(output)
        print(f"File size: {size} bytes")
    else:
        print("Failure: Output not created.")

if __name__ == "__main__":
    test()
