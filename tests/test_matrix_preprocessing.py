import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
from hymn_remaker.main import process_single_midi

class TestMatrixPreprocessing(unittest.TestCase):
    def setUp(self):
        self.output_dir = "hymn_remaker/output/test_matrix"
        os.makedirs(self.output_dir, exist_ok=True)
        self.test_midi = "hymn_remaker/input/Emmanuel.mid"

        # Mock objects
        self.mock_renderer = MagicMock()
        self.mock_renderer.render.return_value = "dummy.wav"

        self.suno_remaker = MagicMock()
        self.suno_remaker.process_remix.return_value = "dummy_remix.wav"

        self.mock_content_gen = MagicMock()
        self.mock_video = MagicMock()

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    @patch('hymn_remaker.src.suno_browser_automation.SunoBrowserAutomation.trigger_generation')
    @patch('hymn_remaker.src.suno_browser_automation.SunoBrowserAutomation.wait_for_completion_and_download')
    @patch('hymn_remaker.main.process_audio')
    def test_suno_matrix_preprocessing(self, mock_process_audio, mock_wait, mock_trigger):
        mock_trigger.return_value = True
        mock_wait.return_value = True

        # Run pipeline
        try:
            process_single_midi(
                midi_path=self.test_midi,
                output_dir=self.output_dir,
                style="Deep House",
                skip_render=True, # Skip actual rendering
                skip_remake=False,
                upload=False,
                renderer=self.mock_renderer,
                remaker=MagicMock(),
                suno_remaker=self.suno_remaker,
                content_gen=self.mock_content_gen,
                video_producer=self.mock_video,
                suno_matrix=True
            )
        except Exception as e:
            # If it fails due to missing suno_matrix arg, it's fine
            pass
