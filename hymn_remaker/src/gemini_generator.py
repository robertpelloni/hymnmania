import os
import json
import logging
import hashlib
import time
import requests
from pathlib import Path

from google import genai
from google.genai import types
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from hymn_remaker import settings

logger = logging.getLogger(__name__)

# Scopes for Gemini API via OAuth
GEMINI_SCOPES = ["https://www.googleapis.com/auth/generative-language.retriever"]

class GeminiContentGenerator:
    def __init__(self, api_key=None, client_secrets_file="client_secrets.json"):
        """Initialize the GeminiContentGenerator using the new google-genai SDK."""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client_secrets_file = client_secrets_file
        self.model_name = "gemini-2.5-flash"
        self.video_model_name = "veo-3.1-generate-preview" # Latest Google video model
        
        try:
            if self.api_key:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"GeminiContentGenerator (SDK v2) initialized with API Key.")
            else:
                logger.warning("GEMINI_API_KEY not set. Attempting OAuth flow for SDK v2...")
                self.client = self._get_oauth_client()
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Client: {e}")
            self.client = None

    def _get_oauth_client(self):
        """Authenticate via Google OAuth2 and return a genai.Client."""
        creds = None
        token_path = "token_gemini.json"
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, GEMINI_SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.client_secrets_file):
                    raise FileNotFoundError(f"Client secrets file not found: {self.client_secrets_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, GEMINI_SCOPES)
                creds = flow.run_local_server(port=0)
                
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        
        # New SDK v2 Client initialization with credentials
        return genai.Client(credentials=creds)

    def analyze_audio_for_content(self, audio_path, hymn_name, style="Deep House"):
        """Upload and analyze audio to generate metadata and lyrics."""
        if not self.client:
            return self._get_offline_fallbacks(hymn_name, style)

        try:
            logger.info(f"Analyzing audio via Gemini 1.5 Pro: {audio_path}")
            
            # 1. Upload the audio file
            audio_file = self.client.files.upload(file=audio_path)

            # 2. Poll for processing
            while audio_file.state.name == "PROCESSING":
                time.sleep(2)
                audio_file = self.client.files.get(name=audio_file.name)

            prompt = (
                f"Analyze this audio of the hymn '{hymn_name}'. "
                f"1. Generate YouTube metadata (title, description, tags) for a {style} remix. "
                f"2. Provide synced lyrics (text, start, end timestamps). "
                f"Format as JSON: {{'metadata': {{...}}, 'lyrics': [...]}}"
            )

            # 3. Generate content
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[audio_file, prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            data = json.loads(response.text)
            
            # 4. Clean up
            self.client.files.delete(name=audio_file.name)
            return data

        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self._get_offline_fallbacks(hymn_name, style)

    def generate_video_veo(self, prompt, image_url, output_path):
        """
        Generate high-fidelity AI video using Google's Veo model.
        
        Args:
            prompt (str): Visual description.
            image_url (str): Input reference image URL.
            output_path (str): Final MP4 destination.
        """
        if not self.client:
            logger.error("Gemini client not initialized for Veo.")
            return None

        try:
            logger.info(f"Generating AI Video via Google Veo: {prompt[:50]}...")
            
            # Note: Veo access requires billing and might be in preview
            # This is the SDK v2 pattern for video generation
            response = self.client.models.generate_video(
                model=self.video_model_name,
                prompt=prompt,
                input_file=types.File(uri=image_url) if image_url.startswith("gs://") else None,
                # If image_url is a standard URL, we might need to download and upload it first
                config=types.GenerateVideoConfig(
                    output_mime_type="video/mp4",
                    fps=24
                )
            )
            
            # Wait for generation (video gen is slow)
            while response.state.name in ("PROCESSING", "PENDING"):
                time.sleep(10)
                response = self.client.models.get_video(name=response.name)

            if response.state.name == "FAILED":
                raise RuntimeError(f"Veo generation failed: {response.error}")

            video_uri = response.video.uri
            logger.info(f"Veo video generated! Downloading from {video_uri}...")
            
            # Download and save
            res = requests.get(video_uri)
            res.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(res.content)
            
            return output_path

        except Exception as e:
            logger.error(f"Veo video generation failed: {e}")
            return None

    def generate_image(self, prompt, output_path=None):
        """
        Generate an image using Google's Imagen 3 model.
        
        Args:
            prompt (str): Image description.
            output_path (str): Optional local path to save the image.
            
        Returns:
            str: URL or local path to the generated image.
        """
        if not self.client:
            logger.error("Gemini client not initialized for Imagen.")
            return None

        try:
            logger.info(f"Generating image via Imagen 3: {prompt[:50]}...")
            
            # Using Imagen 4 (imagen-4.0-generate-001)
            response = self.client.models.generate_images(
                model="imagen-4.0-generate-001",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/png"
                )
            )
            
            if not response.generated_images:
                raise RuntimeError("Imagen 3 returned no images.")

            # Get the first image
            generated_image = response.generated_images[0]
            
            # If no output path, return the image object or a temp path
            if not output_path:
                output_path = f"temp_art_{hashlib.md5(prompt.encode()).hexdigest()}.png"

            # Save image data
            with open(output_path, "wb") as f:
                f.write(generated_image.image.image_bytes)
                
            logger.info(f"Imagen 3 image saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Imagen 3 generation failed: {e}")
            return None

    def generate_art_prompt(self, audio_data, style="Deep House"):
        title = audio_data.get("metadata", {}).get("title", "Hymn Remix")
        return f"Abstract album art for '{title}'. Style: {style}, modern, sacred, high quality, digital art, vibrant colors."

    def _get_offline_fallbacks(self, hymn_name, style):
        """Standard offline fallbacks without OpenAI dependency."""
        return {
            "metadata": {
                "title": f"{hymn_name} ({style} Remix)",
                "description": f"A modern {style} remix of the classic hymn '{hymn_name}'.",
                "tags": [hymn_name, style, "remix", "hymn", "electronic"]
            },
            "lyrics": [
                {"text": f"--- {hymn_name} ---", "start": 0.0, "end": 4.0},
                {"text": f"[{style} Instrumental]", "start": 4.0, "end": 10.0}
            ]
        }

if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    gen = GeminiContentGenerator()
    # test_file = "hymn_remaker/output/Emmanuel_base.wav"
    # if os.path.exists(test_file):
    #    print(gen.analyze_audio_for_content(test_file, "Emmanuel"))
