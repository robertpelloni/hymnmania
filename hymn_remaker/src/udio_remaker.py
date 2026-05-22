"""
Udio AI Music Remaker - Deep House generation via Udio (Remix/Extend mode).
Uses the unofficial udio-wrapper library with internal API enhancements.
"""
import os
import time
import logging
import requests
import hashlib
import subprocess
from udio_wrapper import UdioWrapper

from hymn_remaker import settings

logger = logging.getLogger(__name__)

class UdioRemaker:
    def __init__(self, auth_token=None):
        self.auth_token = auth_token or settings.UDIO_AUTH_TOKEN
        self.client = None
        if self.auth_token:
            self.client = UdioWrapper(self.auth_token)
            logger.info("UdioRemaker initialized with Auth Token.")
        else:
            logger.warning("UDIO_AUTH_TOKEN not set. UdioRemaker will not function.")

    def is_available(self):
        return self.client is not None

    def _upload_to_tmpfiles(self, file_path):
        """Upload a file anonymously to tmpfiles.org and return a direct download URL."""
        url = "https://tmpfiles.org/api/v1/upload"
        try:
            logger.info(f"Uploading {os.path.basename(file_path)} to tmpfiles.org for Udio access...")
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(url, files=files, timeout=60)
                response.raise_for_status()
                data = response.json()
                if data.get("status") == "success":
                    viewer_url = data["data"]["url"]
                    # Convert to direct download link
                    dl_url = viewer_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                    logger.info(f"Upload complete. Direct download URL: {dl_url}")
                    return dl_url
        except Exception as e:
            logger.error(f"Failed to upload {file_path} to tmpfiles.org: {e}")
        return None

    def remake(self, wav_path, prompt, variance=0.25):
        """
        Remix the hymn audio using Udio's conditioning/remix feature.
        """
        if not self.client:
            raise RuntimeError("Udio client not initialized.")

        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"Audio file not found: {wav_path}")

        try:
            # 1. Upload to Public Bridge
            public_audio_url = self._upload_to_tmpfiles(wav_path)
            if not public_audio_url:
                raise RuntimeError("Could not upload audio to temporary public hosting for Udio.")

            # 2. Trigger Remix via Internal API (studio/create)
            # We use the internal studio/create endpoint to force REMIX mode
            # which handles audio conditioning much better than standard extend.
            logger.info(f"Triggering Udio REMIX with variance {variance}...")
            
            full_prompt = f"{prompt}. REMIX strictly following the melody provided. Deep House."
            
            payload = {
                "prompt": full_prompt,
                "lyrics": "",
                "lyrics_type": "instrumental",
                "seed": -1,
                "variance": variance,
                "model_type": "studio32-v1.5",
                "config": {
                    "mode": "manual",
                    "audio_conditioning_path": public_audio_url,
                    "audio_conditioning_type": "upload",
                    "clip_start": 0.0,
                    "duration": 32
                }
            }

            # Submit generation
            res = self.client.make_request("POST", "studio/create", json_data=payload)
            
            # The API returns a list of track IDs or objects
            if not res:
                raise RuntimeError(f"Udio remix request failed. Response: {res}")
            
            # Extract track ID (handle different response formats)
            track_id = None
            if isinstance(res, list) and len(res) > 0:
                track_id = res[0] if isinstance(res[0], str) else res[0].get("id")
            elif isinstance(res, dict):
                track_id = res.get("id") or res.get("track_id")
            
            if not track_id:
                # If we can't find an ID, fall back to the wrapper's blocking extend() 
                # which we know works but might be less precise.
                logger.warning("Could not parse internal track ID, falling back to wrapper's extend().")
                return self._remake_via_extend(wav_path, public_audio_url, prompt, variance)

            logger.info(f"Remix started. Track ID: {track_id}. Polling for completion...")

            # 3. Poll for completion and download
            final_audio_url = None
            start_time = time.time()
            while time.time() - start_time < settings.UDIO_POLL_TIMEOUT:
                status_data = self.client.get_song_status(track_id)
                status = status_data.get("status", "unknown").lower()
                
                if status == "success" or (status == "unknown" and status_data.get("audio_url")):
                    final_audio_url = status_data.get("audio_url")
                    break
                elif status == "failed":
                    raise RuntimeError(f"Udio generation failed: {status_data.get('error', 'Unknown error')}")
                
                logger.info(f"  Udio Status: {status} ({int(time.time() - start_time)}s)")
                time.sleep(settings.UDIO_POLL_INTERVAL)

            if not final_audio_url:
                raise TimeoutError("Udio remix polling timed out.")

            # 4. Download and Convert
            output_dir = os.path.dirname(wav_path)
            hymn_name = os.path.basename(wav_path).replace("_base.wav", "")
            final_path = os.path.join(output_dir, f"{hymn_name}_remake.wav")
            
            logger.info(f"Downloading and converting Udio track to WAV...")
            mp3_data = requests.get(final_audio_url).content
            temp_mp3 = f"temp_remake_{track_id}.mp3"
            with open(temp_mp3, "wb") as f:
                f.write(mp3_data)
                
            conv_cmd = [settings.FFMPEG_BIN, "-y", "-i", temp_mp3, final_path]
            subprocess.run(conv_cmd, check=True, capture_output=True)
            os.remove(temp_mp3)

            logger.info(f"Udio REMIX finalized at {final_path}")
            return final_path

        except Exception as e:
            logger.error(f"Udio remake failed: {e}")
            raise

    def _remake_via_extend(self, wav_path, audio_url, prompt, variance):
        """Standard wrapper call as a reliable fallback."""
        full_prompt = f"{prompt}. REMIX strictly following the melody provided."
        result = self.client.extend(
            prompt=full_prompt,
            audio_conditioning_path=audio_url,
            seed=-1,
            variance=variance
        )
        
        if not result:
            raise RuntimeError("Fallback extend failed.")
            
        # Resolved via directory search as in original logic
        download_dir = "extend_songs"
        time.sleep(5) # Give it a moment to finalize download
        mp3_files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if f.endswith(".mp3")]
        if not mp3_files:
            raise FileNotFoundError("Could not find downloaded file in extend_songs/")
            
        latest_mp3 = max(mp3_files, key=os.path.getmtime)
        output_dir = os.path.dirname(wav_path)
        hymn_name = os.path.basename(wav_path).replace("_base.wav", "")
        final_path = os.path.join(output_dir, f"{hymn_name}_remake.wav")
        
        subprocess.run([settings.FFMPEG_BIN, "-y", "-i", latest_mp3, final_path], check=True, capture_output=True)
        return final_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    remaker = UdioRemaker()
