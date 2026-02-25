import unittest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hymn_remaker.src.remaker import MusicRemaker

class TestMusicRemaker(unittest.TestCase):
    def setUp(self):
        # Create a dummy audio file
        self.audio_path = "test_input.wav"
        with open(self.audio_path, "wb") as f:
            f.write(b'RIFF....WAVEfmt ....data....')

    def tearDown(self):
        if os.path.exists(self.audio_path):
            os.remove(self.audio_path)

    @patch('hymn_remaker.src.remaker.replicate')
    def test_remake_calls_replicate_run(self, mock_replicate):
        mock_replicate.run.return_value = "http://example.com/remake.wav"

        # Instantiate with a dummy token
        remaker = MusicRemaker(api_token="dummy_token")

        url = remaker.remake(self.audio_path, "Techno")

        self.assertEqual(url, "http://example.com/remake.wav")
        mock_replicate.run.assert_called_once()

        # Verify the args passed to run
        args, kwargs = mock_replicate.run.call_args
        self.assertIn("meta/musicgen", args[0])
        self.assertIn("prompt", kwargs['input'])
        self.assertEqual(kwargs['input']['prompt'], "Techno")

    def test_missing_token_warning(self):
        with patch.dict(os.environ, {}, clear=True):
            # This should log a warning but not crash init
            remaker = MusicRemaker()
            self.assertIsNone(remaker.api_token)

if __name__ == '__main__':
    unittest.main()
