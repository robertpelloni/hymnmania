import unittest
import os
import shutil
import sys
from unittest.mock import patch

# Adjust path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hymn_remaker.src.midi_renderer import MidiRenderer

class TestMidiRenderer(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(__file__)
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        # Create a dummy midi file for testing
        self.midi_path = os.path.join(self.output_dir, "test.mid")
        with open(self.midi_path, "wb") as f:
            f.write(b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x60')

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    @patch('hymn_remaker.src.midi_renderer.NATIVE_ENGINE_AVAILABLE', False)
    @patch('hymn_remaker.src.midi_renderer.subprocess.run')
    @patch('hymn_remaker.src.midi_renderer._find_fluidsynth_bin')
    def test_render_calls_midi_to_audio(self, mock_find_bin, mock_run):
        # Setup mock
        mock_find_bin.return_value = "/usr/bin/fluidsynth"
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""

        renderer = MidiRenderer()
        output_path = os.path.join(self.output_dir, "test.wav")

        # Mock os.path.exists so that the method thinks the output file was created
        original_exists = os.path.exists
        with patch('os.path.exists') as mock_exists:
            # We want exists to return True for the output path, but let other calls (like the input file) behave normally or just mock it to return True always for simplicity here since we know the input file exists.
            def side_effect(path):
                if path == output_path:
                    return True
                return original_exists(path)
            mock_exists.side_effect = side_effect

            renderer.render(self.midi_path, output_path)

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertIn("/usr/bin/fluidsynth", args[0])
        self.assertIn("-F", args[0])
        self.assertIn(os.path.abspath(output_path), args[0])
        self.assertIn(os.path.abspath(self.midi_path), args[0])

    def test_render_missing_midi(self):
        with patch('hymn_remaker.src.midi_renderer.NATIVE_ENGINE_AVAILABLE', False), patch('hymn_remaker.src.midi_renderer._find_fluidsynth_bin', return_value="/usr/bin/fluidsynth"):
            renderer = MidiRenderer()
            with self.assertRaises(FileNotFoundError):
                renderer.render("non_existent.mid", "output.wav")

if __name__ == '__main__':
    unittest.main()
