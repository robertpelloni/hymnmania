"""
Udio AI Music Remaker - Official API Integration via OAuth 2.0.
Supports the 2026 Enterprise API for high-fidelity 48kHz audio.
"""
import os
import time
import logging
import requests
import subprocess
from pathlib import Path
from requests_oauthlib import OAuth2Session

from hymn_remaker import settings

logger = logging.getLogger(__name__)

# Official Udio API v1 Endpoints (2026 standard)
UDIO_AUTH_URL = "https://www.udio.com/api/v1/auth/authorize"
UDIO_TOKEN_URL = "https://www.udio.com/api/v1/auth/token"
UDIO_API_BASE = "https://api.udio.com/v1/"

class UdioOAuthRemaker:
    def __init__(self, client_id=None, client_secret=None, token=None):
        self.client_id = client_id or os.environ.get("UDIO_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("UDIO_CLIENT_SECRET")
        self.token = token
        self.session = None
        
        if self.client_id and self.client_secret:
            self._authenticate()
        else:
            logger.warning("UDIO_CLIENT_ID or CLIENT_SECRET not set. OAuth Remaker will not function.")

    def _authenticate(self):
        """Perform OAuth2 authentication."""
        try:
            if self.token:
                self.session = OAuth2Session(self.client_id, token=self.token)
            else:
                # For machine-to-machine/enterprise access (Client Credentials)
                # Note: If Udio requires Authorization Code flow, we would handle it here.
                from oauthlib.oauth2 import BackendApplicationClient
                client = BackendApplicationClient(client_id=self.client_id)
                self.session = OAuth2Session(client=client)
                self.token = self.session.fetch_token(
                    token_url=UDIO_TOKEN_URL,
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
            logger.info("UdioOAuthRemaker authenticated successfully.")
        except Exception as e:
            logger.error(f"Udio OAuth authentication failed: {e}")
            self.session = None

    def is_available(self):
        return self.session is not None

    def remake(self, wav_path, prompt, variance=0.25):
        """
        Remix the hymn audio using Udio's official API conditioning.
        """
        if not self.session:
            raise RuntimeError("Udio OAuth session not initialized.")

        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"Audio file not found: {wav_path}")

        try:
            # 1. Upload audio as reference (Official API pattern)
            logger.info(f"Uploading reference audio to Udio API: {os.path.basename(wav_path)}")
            
            with open(wav_path, "rb") as f:
                # Request upload slot
                upload_res = self.session.post(
                    f"{UDIO_API_BASE}uploads",
                    json={
                        "filename": os.path.basename(wav_path),
                        "content_type": "audio/wav"
                    }
                )
                upload_res.raise_for_status()
                upload_data = upload_res.json()
                
                upload_id = upload_data.get("id")
                s3_url = upload_data.get("upload_url")
                
                # Upload to S3
                logger.info("  Uploading to Udio storage...")
                requests.put(s3_url, data=f, headers={"Content-Type": "audio/wav"})
                
            # 2. Trigger Remix
            logger.info(f"Triggering remix generation (variance={variance})...")
            gen_res = self.session.post(
                f"{UDIO_API_BASE}generate",
                json={
                    "prompt": f"{prompt}. REMIX strictly following the melody provided.",
                    "model": "udio-v4-remix",
                    "conditioning_id": upload_id,
                    "variance": variance,
                    "config": {
                        "mode": "manual",
                        "duration": 32,
                        "audio_fidelity": "48khz"
                    }
                }
            )
            gen_res.raise_for_status()
            task_id = gen_res.json().get("task_id")
            
            # 3. Poll for completion
            logger.info(f"Remix task started: {task_id}. Polling...")
            start_time = time.time()
            audio_url = None
            
            while time.time() - start_time < settings.UDIO_POLL_TIMEOUT:
                status_res = self.session.get(f"{UDIO_API_BASE}tasks/{task_id}")
                status_data = status_res.json()
                status = status_data.get("status", "").lower()
                
                if status == "completed":
                    audio_url = status_data.get("result", {}).get("audio_url")
                    break
                elif status == "failed":
                    raise RuntimeError(f"Udio API task failed: {status_data.get('error')}")
                
                logger.info(f"  Status: {status} ({int(time.time() - start_time)}s)")
                time.sleep(settings.UDIO_POLL_INTERVAL)
                
            if not audio_url:
                raise TimeoutError("Udio API remake timed out.")

            # 4. Download and process
            output_dir = os.path.dirname(wav_path)
            hymn_name = os.path.basename(wav_path).replace("_base.wav", "")
            final_path = os.path.join(output_dir, f"{hymn_name}_remake.wav")
            
            logger.info(f"Downloading Udio v4 remake...")
            audio_data = requests.get(audio_url).content
            temp_file = f"temp_udio_{task_id}.wav"
            with open(temp_file, "wb") as f:
                f.write(audio_data)
                
            # Final conversion to match project sample rate
            conv_cmd = [
                settings.FFMPEG_BIN, "-y",
                "-i", temp_file,
                "-ar", "44100", "-ac", "2",
                final_path
            ]
            subprocess.run(conv_cmd, check=True, capture_output=True)
            os.remove(temp_file)
            
            logger.info(f"Udio OAuth remake finalized at {final_path}")
            return final_path

        except Exception as e:
            logger.error(f"Udio API remake failed: {e}")
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # remaker = UdioOAuthRemaker()
