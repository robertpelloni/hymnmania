import os
from midi2audio import FluidSynth
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MidiRenderer:
    def __init__(self, soundfont_path=None):
        """
        Initialize the MidiRenderer with a soundfont.

        Args:
            soundfont_path (str): Path to the .sf2 soundfont file.
                                  Defaults to '/usr/share/sounds/sf2/FluidR3_GM.sf2' if not provided.
        """
        if soundfont_path:
            self.soundfont_path = soundfont_path
        else:
            # Try to find a default soundfont
            default_paths = [
                '/usr/share/sounds/sf2/FluidR3_GM.sf2',
                '/usr/share/sounds/sf2/default-GM.sf2',
                '/usr/share/soundfonts/default.sf2'
            ]
            for path in default_paths:
                if os.path.exists(path):
                    self.soundfont_path = path
                    break
            else:
                raise FileNotFoundError("No default soundfont found. Please provide a path to a valid .sf2 file.")

        logger.info(f"Using SoundFont: {self.soundfont_path}")
        self.fs = FluidSynth(self.soundfont_path)

    def render(self, midi_path, output_path):
        """
        Render a MIDI file to audio (WAV/MP3/FLAC depending on extension).

        Args:
            midi_path (str): Path to the input MIDI file.
            output_path (str): Path to the output audio file.
        """
        if not os.path.exists(midi_path):
            raise FileNotFoundError(f"MIDI file not found: {midi_path}")

        logger.info(f"Rendering {midi_path} to {output_path}...")

        try:
            # midi2audio mainly supports play_midi (to speakers) or midi_to_audio (to file)
            # The output format is determined by the file extension if midi2audio supports it,
            # but usually it renders to WAV and then converts if needed.
            # midi2audio uses 'flac' by default if not specified in method name, but let's check.
            # Actually midi2audio has `midi_to_audio(midi_file, audio_file)`

            self.fs.midi_to_audio(midi_path, output_path)
            logger.info("Rendering complete.")

        except Exception as e:
            logger.error(f"Failed to render MIDI: {e}")
            raise

if __name__ == "__main__":
    # Test execution
    import sys
    if len(sys.argv) > 2:
        renderer = MidiRenderer()
        renderer.render(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python midi_renderer.py <input.mid> <output.wav>")
