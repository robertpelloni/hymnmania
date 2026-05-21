import os
import time
import logging
import requests
from pathlib import Path

from hymn_remaker import settings
from hymn_remaker.src.udio_api import UdioAPIClient
from hymn_remaker.src.udio_browser_automation import UdioBrowserAutomation

logger = logging.getLogger(__name__)

class UdioRemaker:
    """Generate remakes of hymn audio using Udio AI."""

    def __init__(self, oauth_token=None, cookie_string=None):
        self.api = UdioAPIClient(oauth_token=oauth_token, cookie_string=cookie_string)
        self.oauth_token = self.api.oauth_token
        self.cookie_string = self.api.cookie_string
        self.browser = UdioBrowserAutomation()

    def is_available(self):
        """Check if Udio API or browser automation is configured."""
        # The service is available if either we have the token configured or Edge is open for automation
        if self.api.is_available():
            return True
        # Check if browser automation port is alive
        targets = self.browser._get_page_targets()
        return len(targets) > 0

    def _wav_to_mp3(self, wav_path, bitrate="192k"):
        """Convert a WAV file to MP3 using ffmpeg."""
        import subprocess
        mp3_path = wav_path.rsplit(".", 1)[0] + ".mp3"
        if os.path.exists(mp3_path):
            logger.info(f"MP3 file already exists at {mp3_path}")
            return mp3_path

        logger.info(f"Compressing base WAV to MP3: {wav_path} -> {mp3_path}...")
        cmd = [
            settings.FFMPEG_BIN,
            "-y", "-i", wav_path,
            "-codec:a", "libmp3lame",
            "-b:a", bitrate,
            "-joint_stereo", "1",
            mp3_path,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg compression failed: {result.stderr[-500:]}")
        return mp3_path

    def remake(self, wav_path, prompt, duration=30, style=None, title=None):
        """Generate a remake of a hymn using Udio AI.

        Automatically uses Edge CDP Browser automation if available to bypass anti-bot,
        falling back to direct backend API proxy if Edge is closed.

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
        
        # Compress WAV to MP3 before uploading
        mp3_path = None
        if wav_path and os.path.exists(wav_path) and wav_path.lower().endswith(".wav"):
            try:
                mp3_path = self._wav_to_mp3(wav_path)
            except Exception as e:
                logger.warning(f"Could not compress WAV to MP3: {e}. Will try to upload original WAV if possible.")

        # Combine prompt and style
        full_prompt = f"{style}, {prompt}" if style else prompt

        track_ids = []
        browser_active = False
        
        # Try browser automation first
        targets = self.browser._get_page_targets()
        if targets:
            logger.info("Microsoft Edge debugger is active. Attempting browser automation...")
            try:
                # 1. Capture existing song IDs via API to identify the newly generated song
                headers = self.api._get_headers(get_request=True)
                existing_ids = set()
                resp = requests.get(f"{self.api.base_url}/api/songs/me?pageSize=5", headers=headers, timeout=10)
                if resp.status_code == 200:
                    existing_ids = {song["id"] for song in resp.json().get("data", [])}
                
                # 2. Trigger the generation inside Edge tab (with reference MP3 upload)
                self.browser.trigger_generation(full_prompt, audio_path=mp3_path or wav_path)
                browser_active = True
                
                # 3. Poll songs list to detect the new generating track IDs
                logger.info("Waiting for Edge to create the new track generation record...")
                start_detect = time.time()
                while time.time() - start_detect < 45:
                    resp = requests.get(f"{self.api.base_url}/api/songs/me?pageSize=5", headers=headers, timeout=10)
                    if resp.status_code == 200:
                        current_songs = resp.json().get("data", [])
                        new_songs = [s for s in current_songs if s["id"] not in existing_ids]
                        if new_songs:
                            track_ids = [s["id"] for s in new_songs]
                            logger.info(f"Browser automation succeeded! Detected new generating tracks: {track_ids}")
                            break
                    time.sleep(2)
                
                if not track_ids:
                    logger.warning("Browser clicked 'Create' but no new track ID was detected in account history.")
            except Exception as e:
                logger.warning(f"Browser automation failed: {e}. Falling back to direct API...")
        
        # Fall back to low-level proxy API if browser is inactive or failed
        if not track_ids:

            logger.info("Using low-level direct API generate-proxy fallback...")
            result = self.api.generate(prompt=prompt, style=style, title=title)
            track_ids = result.get("track_ids")
            if not track_ids:
                raise RuntimeError(f"Failed to get track IDs from Udio response: {result}")
            logger.info(f"Direct API generation started for tracks: {track_ids}")

        # Polling for completion
        logger.info(f"Polling for track completion: {track_ids}...")
        audio_url = self.api.poll_until_ready(track_ids)
        
        if not audio_url:
            raise RuntimeError(f"No audio URL returned for tracks {track_ids}")

        # Download the result
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
