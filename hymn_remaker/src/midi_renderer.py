import os
import sys
import logging
import subprocess
import math
import time

from hymn_remaker import settings

# Ensure the root directory is in sys.path so we can import hymn_player_ext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def _check_native_engine():
    try:
        import hymn_player_ext
        return True
    except ImportError:
        return False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _find_fluidsynth_bin():
    """Find the fluidsynth executable. Checks settings.FLUIDSYNTH_BIN first, then PATH."""
    local_bin = settings.FLUIDSYNTH_BIN
    if os.path.isfile(local_bin):
        return local_bin

    import shutil
    system_bin = shutil.which("fluidsynth")
    if system_bin:
        return system_bin

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
        if soundfont_path:
            self.soundfont_path = soundfont_path
        else:
            env_path = os.environ.get('SOUNDFONT_PATH')
            if env_path and os.path.exists(env_path):
                self.soundfont_path = env_path
            else:
                for path in settings.DEFAULT_SOUNDFONT_PATHS:
                    if os.path.exists(path):
                        self.soundfont_path = path
                        break
                else:
                    raise FileNotFoundError("No default soundfont found.")

        logger.info(f"Using SoundFont: {self.soundfont_path}")
        self.fluidsynth_bin = _find_fluidsynth_bin()
        if self.fluidsynth_bin:
            logger.info(f"FluidSynth CLI: {self.fluidsynth_bin}")
        else:
            logger.warning("FluidSynth CLI binary not found.")

    def _get_midi_duration(self, midi_path):
        import mido
        try:
            mid = mido.MidiFile(midi_path)
            return mid.length
        except Exception:
            return 120.0

    def get_midi_bpm(self, midi_path):
        import mido
        try:
            mid = mido.MidiFile(midi_path)
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'set_tempo':
                        return mido.tempo2bpm(msg.tempo)
            return 120.0
        except Exception:
            return 120.0

    def _render_fluidsynth_cli(self, midi_path, output_path, transient_mode=False):
        if not self.fluidsynth_bin:
            raise FileNotFoundError("FluidSynth binary not found.")

        import mido
        render_midi = midi_path
        if transient_mode:
            try:
                mid = mido.MidiFile(midi_path)
                new_mid = mido.MidiFile()
                for track in mid.tracks:
                    new_track = mido.MidiTrack()
                    new_track.append(mido.Message('program_change', program=115, time=0))
                    for msg in track:
                        new_track.append(msg.copy() if hasattr(msg, 'copy') else msg)
                    new_mid.tracks.append(new_track)
                
                temp_transient_midi = midi_path.replace(".mid", "_transient.mid")
                new_mid.save(temp_transient_midi)
                render_midi = temp_transient_midi
                logger.info(f"Transient mode enabled.")
            except Exception as e:
                logger.warning(f"Failed to create transient MIDI: {e}")

        cmd = [
            self.fluidsynth_bin,
            '-F', os.path.abspath(output_path),
            '-r', str(settings.SAMPLE_RATE),
            '-ni',
            os.path.abspath(self.soundfont_path),
            os.path.abspath(render_midi),
        ]

        logger.info(f"Running FluidSynth CLI: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if transient_mode and render_midi != midi_path and os.path.exists(render_midi):
            os.remove(render_midi)

        if result.returncode != 0:
            raise RuntimeError(f"FluidSynth CLI failed: {result.stderr[:500]}")

    def render(self, midi_path, output_path, transient=False, transient_only=False):
        if not os.path.exists(midi_path):
            raise FileNotFoundError(f"MIDI file not found: {midi_path}")

        if transient_only:
            try:
                from pipeline.processing.sonic_vacuum import SonicVacuumProcessor
                vacuum = SonicVacuumProcessor(midi_path)
                vacuum.render_dry_piano(output_path)
                return
            except Exception:
                pass
        
        try:
            if _check_native_engine():
                import hymn_player_ext
                import soundfile as sf
                import numpy as np
                if transient:
                    self._render_fluidsynth_cli(midi_path, output_path, transient_mode=True)
                else:
                    player = hymn_player_ext.HymnPlayer(self.soundfont_path)
                    if not player.load(midi_path):
                        raise RuntimeError("Failed to load MIDI.")

                    duration_sec = self._get_midi_duration(midi_path)
                    sample_rate = settings.SAMPLE_RATE
                    total_frames = math.ceil((duration_sec + settings.REVERB_TAIL_SECONDS) * sample_rate)

                    player.play()
                    chunk_size = settings.SAMPLE_RATE
                    all_audio = []
                    rendered = 0
                    while rendered < total_frames and player.is_playing():
                        all_audio.append(player.render_audio(chunk_size))
                        rendered += chunk_size
                    player.stop()

                    final_audio = np.concatenate(all_audio).reshape(-1, 2)
                    max_val = np.max(np.abs(final_audio))
                    if max_val > 1.0: final_audio /= max_val
                    sf.write(output_path, final_audio, sample_rate)
            else:
                self._render_fluidsynth_cli(midi_path, output_path, transient_mode=transient)
        except Exception as e:
            logger.error(f"Render failed: {e}")
            self._render_fluidsynth_cli(midi_path, output_path, transient_mode=transient)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        MidiRenderer().render(sys.argv[1], sys.argv[2])
