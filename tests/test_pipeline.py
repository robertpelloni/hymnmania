import unittest
import os
import mido
import sys

# Ensure parent directory is in path for imports
sys.path.append(os.getcwd())

from pipeline.processing.sonic_vacuum import SonicVacuumProcessor
from pipeline.processing.symbolic_norm import SymbolicNormalizer
from pipeline.processing.house_quantizer import HouseStructuralQuantizer

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.test_midi = "hymn_remaker/input/Emmanuel.mid"
        os.makedirs("hymn_remaker/output", exist_ok=True)

    def test_sonic_vacuum(self):
        output = "hymn_remaker/output/test_vacuum.wav"
        vacuum = SonicVacuumProcessor(self.test_midi)
        vacuum.render_dry_piano(output)
        self.assertTrue(os.path.exists(output))

    def test_symbolic_norm(self):
        output = "hymn_remaker/output/test_norm.mid"
        norm = SymbolicNormalizer(self.test_midi)
        norm.normalize(output)
        self.assertTrue(os.path.exists(output))
        mid = mido.MidiFile(output)
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    self.assertEqual(msg.velocity, 100)

    def test_house_quantizer(self):
        output = "hymn_remaker/output/test_house.mid"
        quantizer = HouseStructuralQuantizer(self.test_midi)
        quantizer.quantize(output)
        self.assertTrue(os.path.exists(output))
        mid = mido.MidiFile(output)
        # Check for Kick track
        track_names = [t.name for t in mid.tracks]
        self.assertIn("Kick", track_names)

if __name__ == '__main__':
    unittest.main()
