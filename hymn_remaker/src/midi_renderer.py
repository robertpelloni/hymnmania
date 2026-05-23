import os
import sys
import logging
import subprocess
import soundfile as sf
import numpy as np
import mido
import math
import time

from hymn_remaker import settings

# Ensure the root directory is in sys.path so we can import hymn_remaker
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    import hymn_player_ext
    NATIVE_ENGINE_AVAILABLE = True
except ImportError:
    NATIVE_ENGINE_AVAILABLE = False
    logging.warning("Native HymnPlayer engine not found. Falling back to FluidSynth CLI. (No module named 'hymn_player_ext')")

logger = logging.getLogger(__name__)


class MidiRenderer:
    def __init__(self, soundfont_path=None):
        self.soundfont_path = soundfont_path or self._find_default_soundfont()
        self.fluidsynth_bin = settings.FLUIDSYNTH_BIN

    def _find_default_soundfont(self):
        """Find the first available soundfont from settings."""
        for path in settings.DEFAULT_SOUNDFONT_PATHS:
            if os.path.exists(path):
                logger.info(f"Using SoundFont: {path}")
                return path
        raise FileNotFoundError("No valid SoundFont file found in default paths.")

    def _get_midi_duration(self, midi_path):
        """Calculate the duration of a MIDI file in seconds."""
        mid = mido.MidiFile(midi_path)
        return mid.length

    def get_midi_bpm(self, midi_path):
        """Extract the average BPM from a MIDI file."""
        try:
            mid = mido.MidiFile(midi_path)
            # Default if no tempo found
            tempo = 500000 # 120 BPM
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'set_tempo':
                        tempo = msg.tempo
                        break
            return mido.tempo2bpm(tempo)
        except Exception:
            return 120.0

    def _render_fluidsynth_cli(self, midi_path, output_path, transient_mode=False):
        """Render MIDI to audio using the FluidSynth CLI directly."""
        if not self.fluidsynth_bin:
            raise FileNotFoundError(
                "FluidSynth binary not found. Install it or place fluidsynth.exe in hymn_remaker/bin/"
            )

        render_midi = midi_path
        
        # In transient mode, we create a temporary "clicky" version of the MIDI
        if transient_mode:
            try:
                mid = mido.MidiFile(midi_path)
                new_mid = mido.MidiFile()
                for track in mid.tracks:
                    new_track = mido.MidiTrack()
                    # Force all channels to Woodblock (Program 115)
                    new_track.append(mido.Message('program_change', program=115, time=0))
                    for msg in track:
                        if msg.type in ('note_on', 'note_off'):
                            new_msg = msg.copy()
                            new_track.append(new_msg)
                        elif not msg.is_meta and msg.type != 'program_change':
                            new_track.append(msg)
                        elif msg.is_meta:
                            new_track.append(msg)
                    new_mid.tracks.append(new_track)
                
                temp_transient_midi = midi_path.replace(".mid", "_transient.mid")
                new_mid.save(temp_transient_midi)
                render_midi = temp_transient_midi
                logger.info(f"Transient mode enabled: Using Woodblock pulses for {midi_path}")
            except Exception as e:
                logger.warning(f"Failed to create transient MIDI: {e}. Using original.")

        # FluidSynth v2.x requires options BEFORE soundfont/midi arguments.
        abs_soundfont = os.path.abspath(self.soundfont_path)
        abs_midi = os.path.abspath(render_midi)
        abs_output = os.path.abspath(output_path)

        cmd = [
            self.fluidsynth_bin,
            '-F', abs_output,
            '-r', str(settings.SAMPLE_RATE),
            '-ni',
            abs_soundfont,
            abs_midi,
        ]

        logger.info(f"Running FluidSynth CLI: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # Cleanup transient file
        if transient_mode and render_midi != midi_path and os.path.exists(render_midi):
            os.remove(render_midi)

        if result.returncode != 0:
            logger.error(f"FluidSynth stderr: {result.stderr}")
            raise RuntimeError(f"FluidSynth CLI failed: {result.stderr[:500]}")

    def render(self, midi_path, output_path, transient_mode=False):
        """
        Render a MIDI file to audio.
        """
        if not os.path.exists(midi_path):
            raise FileNotFoundError(f"MIDI file not found: {midi_path}")

        logger.info(f"Rendering {midi_path} to {output_path} (transient={transient_mode})...")
        
        try:
            if NATIVE_ENGINE_AVAILABLE:
                if transient_mode:
                    self._render_fluidsynth_cli(midi_path, output_path, transient_mode=True)
                else:
                    logger.info("Using Native C++ Engine for rendering.")
                    player = hymn_player_ext.HymnPlayer(self.soundfont_path)

                    if not player.load(midi_path):
                        raise RuntimeError("Failed to load MIDI file into native engine.")

                    duration_sec = self._get_midi_duration(midi_path)
                    sample_rate = settings.SAMPLE_RATE
                    total_frames = math.ceil((duration_sec + settings.REVERB_TAIL_SECONDS) * sample_rate)

                    player.play()
                    chunk_size = settings.SAMPLE_RATE
                    frames_rendered = 0
                    all_audio = []

                    while frames_rendered < total_frames and player.is_playing():
                        audio_chunk = player.render_audio(chunk_size)
                        all_audio.append(audio_chunk)
                        frames_rendered += chunk_size

                    player.stop()

                    if not all_audio:
                        raise RuntimeError("Native engine rendered zero audio frames.")

                    final_audio = np.concatenate(all_audio).reshape(-1, 2)
                    max_val = np.max(np.abs(final_audio))
                    if max_val > 1.0:
                        final_audio = final_audio / max_val

                    sf.write(output_path, final_audio, sample_rate)
                    logger.info("Native rendering complete.")
            else:
                logger.info("Using FluidSynth CLI fallback for rendering.")
                self._render_fluidsynth_cli(midi_path, output_path, transient_mode=transient_mode)

        except Exception as e:
            logger.error(f"Failed to render MIDI: {e}")
            raise


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        renderer = MidiRenderer()
        renderer.render(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python midi_renderer.py <input.mid> <output.wav>")
