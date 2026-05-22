"""
Udio AI Music Remaker - Deep House generation via Udio.
Uses the udio-wrapper library with monkey-patched headers for 2026 session compatibility,
and supports CDP-based Edge automation for the most robust advanced control.
"""
import os
import time
import logging
import subprocess
import glob
from pathlib import Path
from udio_wrapper import UdioWrapper
from hymn_remaker.src.udio_browser_automation import UdioBrowserAutomation

from hymn_remaker import settings

logger = logging.getLogger(__name__)

class UdioRemaker:
    def __init__(self, auth_token=None, cookie_string=None):
        self.auth_token = auth_token or settings.UDIO_AUTH_TOKEN
        # cookie_string is currently ignored by UdioWrapper but accepted for compat
        self.client = None
        if self.auth_token:
            self.client = UdioWrapper(self.auth_token)
            self._apply_2026_patches()
            logger.info("UdioRemaker initialized with Auth Token and 2026 patches.")
        
        # Initialize CDP automation for Edge
        self.edge_auto = UdioBrowserAutomation()

    def _apply_2026_patches(self):
        """Monkey-patch the udio-wrapper to use correct 2026 cookie naming and headers."""
        if not self.client:
            return

        auth_token = self.auth_token
        cookie0 = os.environ.get("UDIO_COOKIE_0", "")
        cookie1 = os.environ.get("UDIO_COOKIE_1", "")

        def patched_get_headers(self_inner, get_request=False):
            cookie_str = f"sb-ssr-production-auth-token.0={cookie0}"
            if cookie1:
                cookie_str += f"; sb-ssr-production-auth-token.1={cookie1}"
            
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}",
                "Cookie": cookie_str,
                "Origin": "https://www.udio.com",
                "Referer": "https://www.udio.com/studio",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
                "X-Udio-Request-Source": "web"
            }
            return headers

        import types
        self.client.get_headers = types.MethodType(patched_get_headers, self.client)
        logger.info("Successfully patched UdioWrapper with 2026 security headers.")

    def is_available(self):
        return self.client is not None or os.environ.get("UDIO_COOKIE_0") is not None

    def _upload_to_bridge(self, file_path):
        import requests
        try:
            logger.info(f"Uploading {os.path.basename(file_path)} to tmpfiles.org bridge...")
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post('https://tmpfiles.org/api/v1/upload', files=files, timeout=60)
                response.raise_for_status()
                data = response.json()
                file_url = data['data']['url']
                direct_url = file_url.replace('https://tmpfiles.org/', 'https://tmpfiles.org/dl/')
                logger.info(f"Bridge upload successful: {direct_url}")
                return direct_url
        except Exception as e:
            logger.error(f"Bridge upload failed: {e}")
            return None

<<<<<<< HEAD
    def remake(self, wav_path, prompt, variance=0.35, mode="auto"):
=======
    def remake(self, wav_path, prompt, variance=0.35, prompt_strength=0.65, manual_mode=True, extension_hack=False):
>>>>>>> origin/feat/psy-mono-pipeline-1.27.0-9908176330949525010
        """
        Remix the hymn audio using either API or Edge CDP mode.
        """
        if mode == "browser":
            return self.remake_edge(wav_path, prompt, variance=variance)
        
        try:
            return self.remake_api(wav_path, prompt, variance=variance)
        except Exception as e:
            if mode == "auto":
                logger.warning(f"API remake failed: {e}. Falling back to Edge Automation mode...")
                return self.remake_edge(wav_path, prompt, variance=variance)
            raise

    def remake_api(self, wav_path, prompt, variance=0.35):
        if not self.client:
            raise RuntimeError("Udio client not initialized for API mode.")

        mp3_upload_path = wav_path.replace(".wav", "_upload.mp3")
        subprocess.run([
            settings.FFMPEG_BIN, "-y", "-i", wav_path,
            "-codec:a", "libmp3lame", "-q:a", "2", mp3_upload_path
        ], check=True, capture_output=True)

        try:
            public_url = self._upload_to_bridge(mp3_upload_path)
            if not public_url: raise RuntimeError("Failed to obtain public URL.")

            full_prompt = f"Deep house, 122 bpm, soulful melodic house, driving 4x4 club beat. [Audio Influence: {variance}]"
            self.client.extend(prompt=full_prompt, audio_conditioning_path=public_url, seed=-1)

            download_dir = "extend_songs"
            time.sleep(5) 
            files = glob.glob(os.path.join(download_dir, "*.mp3"))
            if not files: raise RuntimeError("No downloaded MP3 found.")
            latest_mp3 = max(files, key=os.path.getmtime)
            
            output_dir = os.path.dirname(wav_path)
            final_path = os.path.join(output_dir, f"{Path(wav_path).stem.replace('_base','')}_remake.wav")
            subprocess.run([settings.FFMPEG_BIN, "-y", "-i", latest_mp3, final_path], check=True, capture_output=True)
            return final_path
        finally:
            if os.path.exists(mp3_upload_path): os.remove(mp3_upload_path)

    def remake_edge(self, wav_path, prompt, variance=0.35):
        """
        Remix using CDP-based Edge automation (driving the active tab).
        """
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"Audio file not found: {wav_path}")

        # 1. Convert to MP3 for upload efficiency
        mp3_upload_path = wav_path.replace(".wav", "_upload.mp3")
        logger.info(f"Preparing MP3 for Edge upload: {os.path.basename(mp3_upload_path)}")
        subprocess.run([
            settings.FFMPEG_BIN, "-y", "-i", wav_path,
            "-codec:a", "libmp3lame", "-q:a", "2", mp3_upload_path
        ], check=True, capture_output=True)

        try:
<<<<<<< HEAD
            logger.info("Triggering Edge Automation (CDP)...")
            tag_prompt = "Deep house, 122 bpm, soulful melodic house, driving 4x4 club beat, crisp analog synthesizer chords, modern polished club mix"
            
            # Using the existing UdioBrowserAutomation class
            success = self.edge_auto.trigger_generation(
                prompt=tag_prompt,
                audio_path=mp3_upload_path,
                variance=variance
            )
            
            if not success:
                raise RuntimeError("Edge automation failed to trigger generation.")

            logger.info("Generation triggered in Edge! Waiting for track completion and auto-download...")
=======
            # Power User Hack: If extension_hack is True, crop the audio to first 15 seconds
            # and use Udio's 'extend' mode instead of 'remix'.
            source_audio = wav_path
            if extension_hack:
                logger.info("Applying Udio Extension Hack: Cropping to 15s...")
                cropped_path = wav_path.replace(".wav", "_crop15.wav")
                crop_cmd = [settings.FFMPEG_BIN, "-y", "-i", wav_path, "-t", "15", cropped_path]
                subprocess.run(crop_cmd, check=True, capture_output=True)
                source_audio = cropped_path

            # 1. Upload to Public Bridge
            public_audio_url = self._upload_to_tmpfiles(source_audio)
            if not public_audio_url:
                raise RuntimeError("Could not upload audio to temporary public hosting for Udio.")

            # 2. Trigger Remix or Extension via Internal API (studio/create)
            if extension_hack:
                logger.info("Triggering Udio EXTENSION...")
                payload = {
                    "prompt": f"{prompt} [Drop] [Full Electronic Instrumentation]",
                    "lyrics": "",
                    "lyrics_type": "instrumental",
                    "seed": -1,
                    "model_type": "studio32-v1.5",
                    "config": {
                        "mode": "manual" if manual_mode else "auto",
                        "audio_conditioning_path": public_audio_url,
                        "audio_conditioning_type": "upload",
                        "extension_type": "after",
                        "duration": 32
                    }
                }
            else:
                logger.info(f"Triggering Udio REMIX with variance {variance}...")
                payload = {
                    "prompt": prompt,
                    "lyrics": "",
                    "lyrics_type": "instrumental",
                    "seed": -1,
                    "variance": variance,
                    "prompt_strength": prompt_strength,
                    "manual_mode": manual_mode,
                    "model_type": "studio32-v1.5",
                    "config": {
                        "mode": "manual" if manual_mode else "auto",
                        "audio_conditioning_path": public_audio_url,
                        "audio_conditioning_type": "upload",
                        "clip_start": 0.0,
                        "duration": 32
                    }
                }
>>>>>>> origin/feat/psy-mono-pipeline-1.27.0-9908176330949525010

            # Use the new active polling and download method
            download_triggered = self.edge_auto.wait_for_completion_and_download(timeout=300)

            if not download_triggered:
                raise RuntimeError("Edge automation failed to trigger track download.")

            # Now poll the Downloads folder for the file we just clicked 'Download' on
            download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            start_time = time.time()
            final_path = None

            logger.info(f"Watching {download_dir} for the downloaded track...")
            while time.time() - start_time < 60: # Short 1 min timeout since download should be active
                files = glob.glob(os.path.join(download_dir, "*.mp3"))
                if files:
                    latest_mp3 = max(files, key=os.path.getmtime)
                    # Use a very short window (30s) to ensure it's the one we just triggered
                    if time.time() - os.path.getmtime(latest_mp3) < 30:
                        final_path = latest_mp3
                        break
                time.sleep(5)

            if not final_path:
                raise RuntimeError("Timed out waiting for file to appear in Downloads folder after click.")

            logger.info(f"Detected Udio download: {final_path}")


            # Finalize
            output_dir = os.path.dirname(wav_path)
            hymn_name = os.path.basename(wav_path).replace("_base.wav", "")
            remake_path = os.path.join(output_dir, f"{hymn_name}_remake.wav")
            subprocess.run([settings.FFMPEG_BIN, "-y", "-i", final_path, remake_path], check=True, capture_output=True)
            
            return remake_path
        finally:
            if os.path.exists(mp3_upload_path): os.remove(mp3_upload_path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    remaker = UdioRemaker()
