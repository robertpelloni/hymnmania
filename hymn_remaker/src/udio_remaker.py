"""
Udio AI Music Remaker — High-level orchestration facade.

This module provides the ``UdioRemaker`` class that the pipeline imports.
"""

import os
import time
import logging
import requests
from pathlib import Path

from hymn_remaker import settings
from hymn_remaker.src.udio_api import UdioAPIClient

logger = logging.getLogger(__name__)

class UdioRemaker:
    """Generate remakes of hymn audio using Udio AI."""

    def __init__(self, oauth_token=None, cookie_string=None):
        self.api = UdioAPIClient(oauth_token=oauth_token, cookie_string=cookie_string)
        self.oauth_token = self.api.oauth_token
        self.cookie_string = self.api.cookie_string

    def is_available(self):
        """Check if Udio API is configured and token is valid."""
        return self.api.is_available()

    def remake(self, wav_path, prompt, duration=30, style=None, title=None):
        """Generate a remake of a hymn using Udio AI.

        Currently focused on text-to-music generation. 
        TODO: Implement audio-to-audio influence if Udio API supports it via proxy.

        Args:
            wav_path (str): Path to the input WAV file.
            prompt (str): Text prompt for the style.
            duration (int): Target duration in seconds.
            style (str): Style tags.
            title (str): Song title.

        Returns:
            str: Path to the downloaded WAV file.
        """
        logger.info(f"Starting Udio remake for {wav_path}...")
        
        # 1. Submit generation request
        # Note: We use the prompt and style as provided.
        # If wav_path influence is supported in the future, we'd upload it here.
        result = self.api.generate(prompt=prompt, style=style, title=title)
        
        track_ids = result.get("track_ids")
            
        if not track_ids:
            raise RuntimeError(f"Failed to get track IDs from Udio response: {result}")

        logger.info(f"Udio generation started for tracks: {track_ids}. Polling for completion...")

        # 2. Poll for completion
        audio_url = self.api.poll_until_ready(track_ids)
        
        if not audio_url:
            raise RuntimeError(f"No audio URL returned for tracks {track_ids}")

        # 3. Download the result
        track_id = track_ids[0]
        output_filename = f"udio_{track_id}.wav"
        output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
        
        logger.info(f"Downloading Udio result from {audio_url}...")
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        logger.info(f"Udio remake saved to {output_path}")
        return output_path
