"""
Udio AI client — HTTP API layer, authentication, and polling.

This module handles direct HTTP communication with the Udio internal API
using the 'sb-api-auth-token' (Supabase JWT) extracted from the browser.
"""

import os
import time
import json
import logging
import requests
from hymn_remaker import settings

logger = logging.getLogger(__name__)

# Udio API endpoints
UDIO_BASE_URL = "https://www.udio.com"
GENERATE_ENDPOINT = "/api/generate-proxy"
SONGS_ENDPOINT = "/api/songs"

class UdioAPIClient:
    """Low-level HTTP client for the Udio AI API.

    Handles authentication headers, song generation requests, 
    and completion polling.
    """

    def __init__(self, oauth_token=None):
        self.oauth_token = oauth_token or os.environ.get("UDIO_OAUTH_TOKEN", "")
        self.base_url = os.environ.get("UDIO_BASE_URL", UDIO_BASE_URL)

        if not self.oauth_token:
            logger.warning("UDIO_OAUTH_TOKEN not set. UdioAPIClient will not function.")
        else:
            logger.info("UdioAPIClient initialized")

    def _get_headers(self, get_request=False):
        """Build request headers with auth token."""
        return {
            "Authorization": f"Bearer {self.oauth_token}",
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
        }

    def is_available(self):
        """Check if Udio API is configured and token is valid."""
        if not self.oauth_token:
            return False
        try:
            headers = self._get_headers(get_request=True)
            # Use the me endpoint as a connectivity test
            url = f"{self.base_url}/api/songs/me?pageSize=1"
            resp = requests.get(
                url,
                headers=headers,
                timeout=10,
            )
            print(f"DEBUG: Udio is_available status={resp.status_code} url={url}")
            return resp.status_code == 200
        except Exception as e:
            print(f"DEBUG: Udio is_available exception={e}")
            return False

    def generate(self, prompt, style=None, title=None, custom_mode=True):
        """Submit a song generation request to Udio.

        Args:
            prompt (str): Lyrics or description prompt.
            style (str): Musical style/genre tags.
            title (str): Song title.
            custom_mode (bool): Whether to use custom mode (lyrics + tags).

        Returns:
            dict: Task or song info from the API.
        """
        if not self.oauth_token:
            raise RuntimeError("UDIO_OAUTH_TOKEN not configured")

        # Combining style and prompt for the Udio prompt if style is provided
        full_prompt = f"{style}, {prompt}" if style else prompt
        
        data = {
            "prompt": full_prompt,
            "samplerOptions": {
                "seed": -1
            }
        }
        if custom_mode:
            data["lyricInput"] = prompt

        logger.info(f"Submitting Udio generation request to {GENERATE_ENDPOINT}...")
        headers = self._get_headers()
        url = f"{self.base_url}{GENERATE_ENDPOINT}"

        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 401:
            raise RuntimeError("UDIO_OAUTH_TOKEN is invalid or expired.")
        if response.status_code != 200:
            raise RuntimeError(f"Udio API error {response.status_code}: {response.text[:300]}")

        return response.json()

    def get_song_status(self, track_ids):
        """Get the status of specific tracks.

        Args:
            track_ids (list): List of track IDs.

        Returns:
            dict: Song data including status and audio URL.
        """
        headers = self._get_headers(get_request=True)
        url = f"{self.base_url}/api/songs?songIds={','.join(track_ids)}"
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None

    def poll_until_ready(self, track_ids, interval=None, timeout=None):
        """Poll the Udio API until the songs are ready.

        Args:
            track_ids (list): The list of track IDs to poll.
            interval (int): Seconds between checks.
            timeout (int): Max seconds to wait.

        Returns:
            str: URL of the first ready audio file.
        """
        interval = interval or settings.UDIO_POLL_INTERVAL
        timeout = timeout or settings.UDIO_POLL_TIMEOUT
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            status_data = self.get_song_status(track_ids)
            if status_data and "songs" in status_data:
                all_finished = all(song.get("finished") for song in status_data["songs"])
                if all_finished:
                    # Return the path/url of the first song
                    return status_data["songs"][0].get("song_path")
            
            time.sleep(interval)
        
        raise TimeoutError(f"Udio generation timed out for tracks {track_ids}")

