import logging
import os
import requests

logger = logging.getLogger(__name__)

class TikTokUploader:
    """
    Handles headless TikTok video uploads using the TikTok Content Posting API.
    Requires TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET.
    """
    def __init__(self):
        self.client_key = os.environ.get("TIKTOK_CLIENT_KEY")
        self.client_secret = os.environ.get("TIKTOK_CLIENT_SECRET")
        self.access_token = os.environ.get("TIKTOK_ACCESS_TOKEN")

    def is_configured(self):
        return bool(self.client_key and self.client_secret and self.access_token)

    def upload(self, video_path, title, privacy="PRIVATE"):
        """
        Uploads a video to TikTok via the Direct Post API.
        Reference: https://developers.tiktok.com/doc/content-posting-api-reference-direct-post/
        """
        if not self.is_configured():
            logger.warning("TikTok API credentials not configured. Skipping upload.")
            return None

        if not os.path.exists(video_path):
            logger.error(f"TikTok upload failed: Video {video_path} not found.")
            return None

        logger.info(f"Initiating TikTok upload for {video_path} (Privacy: {privacy})")

        # Step 1: Initialize Upload
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        }

        file_size = os.path.getsize(video_path)

        init_payload = {
            "post_info": {
                "title": title,
                "privacy_level": privacy,
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": file_size, # For simplicity, uploading in one chunk if small enough
                "total_chunk_count": 1
            }
        }

        try:
            # 1. Initialize upload
            init_res = requests.post(init_url, headers=headers, json=init_payload)
            init_res.raise_for_status()
            data = init_res.json()

            publish_id = data.get("data", {}).get("publish_id")
            upload_url = data.get("data", {}).get("upload_url")

            if not upload_url:
                logger.error(f"Failed to get TikTok upload URL: {data}")
                return None

            logger.info(f"Got TikTok upload URL for publish_id: {publish_id}")

            # 2. Upload video file
            with open(video_path, 'rb') as f:
                video_data = f.read()

            upload_headers = {
                "Content-Range": f"bytes 0-{file_size-1}/{file_size}",
                "Content-Type": "video/mp4"
            }

            upload_res = requests.put(upload_url, headers=upload_headers, data=video_data)
            upload_res.raise_for_status()

            logger.info("TikTok upload successful!")
            return publish_id

        except requests.exceptions.RequestException as e:
            logger.error(f"TikTok upload API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected TikTok upload error: {e}")
            return None
