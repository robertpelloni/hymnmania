import os
import torch
import torchaudio
import logging
from transformers import MusicgenMelodyForConditionalGeneration, AutoProcessor
import numpy as np
from scipy.io import wavfile

logger = logging.getLogger(__name__)

class LocalMusicRemaker:
    def __init__(self, model_id="facebook/musicgen-melody"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Local MusicGen model ({model_id}) on {self.device}...")
        self.model = MusicgenMelodyForConditionalGeneration.from_pretrained(model_id).to(self.device)
        self.processor = AutoProcessor.from_pretrained(model_id)

    def generate(self, melody_path, prompt, duration=30, output_path=None):
        """
        Generate audio locally using MusicGen melody-conditioned model.
        """
        if not os.path.exists(melody_path):
            raise FileNotFoundError(f"Melody file not found: {melody_path}")

        logger.info(f"Local Generation: prompt='{prompt}', conditioning={melody_path}")

        # Load melody
        melody, sr = torchaudio.load(melody_path)

        # Prepare inputs
        inputs = self.processor(
            audio=melody,
            sampling_rate=sr,
            text=[prompt],
            padding=True,
            return_tensors="pt",
        ).to(self.device)

        # Generate
        # duration in seconds corresponds approximately to max_new_tokens
        # MusicGen uses 50 tokens per second
        max_tokens = int(duration * 50)

        with torch.no_grad():
            audio_values = self.model.generate(**inputs, max_new_tokens=max_tokens)

        # Post-process
        sampling_rate = self.model.config.audio_encoder.sampling_rate
        audio_data = audio_values[0, 0].cpu().numpy()

        if output_path:
            # Normalize to 16-bit PCM
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
            wavfile.write(output_path, sampling_rate, (audio_data * 32767).astype(np.int16))
            logger.info(f"Local generation saved to {output_path}")
            return output_path

        return audio_data, sampling_rate

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Basic test
    # remaker = LocalMusicRemaker()
