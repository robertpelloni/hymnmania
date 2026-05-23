import os
import json
import logging
import hashlib
import time
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class GeminiContentGenerator:
    def __init__(self, api_key=None, client_secrets_file="client_secrets.json"):
        """Initialize the GeminiContentGenerator."""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client_secrets_file = client_secrets_file
        self.model_name = "gemini-2.0-flash"
        self.image_model_name = "imagen-3.0-generate-001"
        self.video_model_name = "veo-2.0-generate-preview" 
        self.client = None
        
    def _get_client(self):
        if self.client: return self.client
        try:
            from google import genai
            if self.api_key:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Gemini Client initialized with API Key.")
            else:
                logger.warning("GEMINI_API_KEY not set. Attempting OAuth flow...")
                if os.path.exists(self.client_secrets_file):
                    self.client = self._get_oauth_client()
                else:
                    logger.error(f"Client secrets file {self.client_secrets_file} not found.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Client: {e}")
        return self.client

    def _get_oauth_client(self):
        """Helper to get an OAuth2-authenticated client using the SDK."""
        from google import genai
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        
        SCOPES = ['https://www.googleapis.com/auth/generative-language']
        creds = None
        token_path = 'gemini_token.json'
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                
        return genai.Client(credentials=creds)

    def analyze_audio_for_content(self, audio_path, hymn_name):
        """Analyze audio to generate visual prompts and themes."""
        client = self._get_client()
        if not client: return None
        
        from google.genai import types
        logger.info(f"Analyzing audio content for {hymn_name}...")
        
        try:
            # Upload audio to Gemini
            with open(audio_path, 'rb') as f:
                audio_file = client.files.upload(file=f, config={"mime_type": "audio/wav"})
            
            prompt = f"Analyze this hymn remake '{hymn_name}' and provide: 1. A short cinematic visual prompt. 2. A central theme quote."
            
            response = client.models.generate_content(
                model=self.model_name,
                contents=[audio_file, prompt]
            )
            
            # Simple parsing
            text = response.text
            logger.info(f"Gemini Analysis: {text[:100]}...")
            return {
                "visual_prompt": text.split('\n')[0],
                "theme": text
            }
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return None

    def generate_image(self, prompt, output_path):
        """Generate a high-quality cover art image."""
        client = self._get_client()
        if not client: return None
        
        from google.genai import types
        logger.info(f"Generating image for prompt: {prompt[:50]}...")
        
        try:
            response = client.models.generate_image(
                model=self.image_model_name,
                prompt=prompt,
                config=types.GenerateImageConfig(
                    number_of_images=1,
                    include_rai_reasoning=True,
                    output_mime_type='image/png'
                )
            )
            
            for i, image in enumerate(response.generated_images):
                with open(output_path, 'wb') as f:
                    f.write(image.image_bytes)
            
            logger.info(f"Image generated and saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gen = GeminiContentGenerator()
