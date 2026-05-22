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

# Ensure the root directory is in sys.path so we can import hymn_player_ext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    import hymn_player_ext
    NATIVE_ENGINE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Native HymnPlayer engine not found. Falling back to FluidSynth CLI. ({e})")
    NATIVE_ENGINE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _find_fluidsynth_bin():
    """Find the fluidsynth executable. Checks settings.FLUIDSYNTH_BIN first, then PATH."""
    # 1. Check the bundled/local path from settings
    local_bin = settings.FLUIDSYNTH_BIN
    if os.path.isfile(local_bin):
        return local_bin

    # 2. Search system PATH
    import shutil
    system_bin = shutil.which("fluidsynth")
    if system_bin:
        return system_bin

    # 3. Check common locations
    candidates = [
        "/usr/bin/fluidsynth",
        "/usr/local/bin/fluidsynth",
        "/opt/homebrew/bin/fluidsynth",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c

    return None


class MidiRenderer:
    def __init__(self, soundfont_path=None):
        """
        Initialize the MidiRenderer with a soundfont.

        Args:
            soundfont_path (str): Path to the .sf2 soundfont file.
                Defaults to searching SOUNDFONT_PATH env var, then
                settings.DEFAULT_SOUNDFONT_PATHS, then bundled soundfonts.
        """
        if soundfont_path:
            self.soundfont_path = soundfont_path
        else:
            # Check SOUNDFONT_PATH env var first
            env_path = os.environ.get('SOUNDFONT_PATH')
            if env_path and os.path.exists(env_path):
                self.soundfont_path = env_path
            else:
                # Try to find a default soundfont from settings
                for path in settings.DEFAULT_SOUNDFONT_PATHS:
                    if os.path.exists(path):
                        self.soundfont_path = path
                        break
                else:
                    raise FileNotFoundError(
                        "No default soundfont found. Please provide a path to a valid .sf2 file. "
                        "Download one to hymn_remaker/soundfonts/ or set SOUNDFONT_PATH env var."
                    )

        logger.info(f"Using SoundFont: {self.soundfont_path}")

        # Find the fluidsynth binary for CLI fallback
        self.fluidsynth_bin = _find_fluidsynth_bin()
        if self.fluidsynth_bin:
            logger.info(f"FluidSynth CLI: {self.fluidsynth_bin}")
        else:
            logger.warning("FluidSynth CLI binary not found. MIDI rendering will fail.")

    def _get_midi_duration(self, midi_path):
        try:
            mid = mido.MidiFile(midi_path)
            return mid.length
        except Exception as e:
            logger.warning(f"Failed to calculate MIDI duration: {e}. Defaulting to 120 seconds.")
            return 120.0

    def stretch_midi(self, input_path, output_path, target_duration=28.0):
        """
        Scale the tempo/ticks of a MIDI file so that it plays within target_duration.
        """
        try:
            mid = mido.MidiFile(input_path)
            original_duration = mid.length
            if original_duration <= 0:
                logger.warning("MIDI duration is 0 or negative. Cannot stretch.")
                return False
                
            scale_factor = target_duration / original_duration
            logger.info(f"Stretching MIDI {input_path} from {original_duration:.2f}s to {target_duration:.2f}s (factor: {scale_factor:.4f})")
            
            for track in mid.tracks:
                for msg in track:
                    if not msg.is_meta or msg.type != 'set_tempo':
                        msg.time = int(round(msg.time * scale_factor))
                        
            mid.save(output_path)
            return True
        except Exception as e:
            logger.error(f"Failed to stretch MIDI: {e}")
            return False


    def get_midi_bpm(self, midi_path):
        """
        Extract the initial BPM from a MIDI file.
        """
        try:
            mid = mido.MidiFile(midi_path)
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'set_tempo':
                        return mido.tempo2bpm(msg.tempo)
            return 120.0  # Default if no tempo found
        except Exception as e:
            logger.warning(f"Failed to extract BPM from MIDI: {e}. Defaulting to 120 BPM.")
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
                            # Shorten note duration for sharp transients
                            new_msg = msg.copy()
                            # Shorten time for note_off or note_on with vel 0
                            if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                                # Limit sustain to very short duration
                                pass 
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

<<<<<<< HEAD
    def render(self, midi_path, output_path, transient_mode=False):
        """
        Render a MIDI file to audio.
=======
        if not os.path.exists(output_path):
            raise RuntimeError(f"FluidSynth completed but output file not found: {output_path}")

        logger.info(f"FluidSynth CLI rendering complete: {output_path}")

    def render(self, midi_path, output_path, transient_only=False):
        """
        Render a MIDI file to audio (WAV/MP3/FLAC depending on extension).

        Args:
            midi_path (str): Path to the input MIDI file.
            output_path (str): Path to the output audio file.
            transient_only (bool): If True, use a sharp, staccato sine-wave sound for AI conditioning.
>>>>>>> origin/feat/psy-mono-pipeline-1.27.0-9908176330949525010
        """
        if not os.path.exists(midi_path):
            raise FileNotFoundError(f"MIDI file not found: {midi_path}")

<<<<<<< HEAD
        logger.info(f"Rendering {midi_path} to {output_path} (transient={transient_mode})...")
        
=======
        logger.info(f"Rendering {midi_path} to {output_path}...")

        if transient_only:
            logger.info("Transient-only rendering requested. Routing to SonicVacuum (Staccato Sines).")
            try:
                from pipeline.processing.sonic_vacuum import SonicVacuumProcessor
                vacuum = SonicVacuumProcessor(midi_path)
                vacuum.render_dry_piano(output_path)
                return
            except Exception as e:
                logger.error(f"SonicVacuum failed: {e}. Falling back to standard render.")

>>>>>>> origin/feat/psy-mono-pipeline-1.27.0-9908176330949525010
        try:
            if NATIVE_ENGINE_AVAILABLE:
                # For transient mode, we stick to CLI for easier MIDI manipulation.
                if transient_mode:
                    self._render_fluidsynth_cli(midi_path, output_path, transient_mode=True)
                else:
                    logger.info("Using Native C++ Engine for rendering.")
                    # Instantiate player locally per thread
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
