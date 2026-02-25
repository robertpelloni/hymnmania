import os
import openai
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self, api_key=None):
        """
        Initialize the ContentGenerator with an OpenAI API key.

        Args:
            api_key (str): OpenAI API key. Defaults to OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set. ContentGenerator will not function.")

        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)

    def generate_metadata(self, hymn_name, style="Deep House"):
        """
        Generate title, description, and tags using GPT-4.

        Args:
            hymn_name (str): Name of the original hymn.
            style (str): The musical style of the remake.

        Returns:
            dict: {
                "title": str,
                "description": str,
                "tags": list
            }
        """
        prompt = (
            f"Generate metadata for a YouTube video featuring a {style} remake of the hymn '{hymn_name}'.\n"
            f"Provide the following fields in JSON format:\n"
            f"1. title: A catchy, modern title for the video.\n"
            f"2. description: A compelling description (max 1000 chars) explaining the remake.\n"
            f"3. tags: A list of 10 relevant tags."
        )

        try:
            logger.info(f"Generating metadata for '{hymn_name}'...")
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",  # Using a model that supports JSON mode
                messages=[
                    {"role": "system", "content": "You are a creative content strategist for a music channel. You must respond in valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )

            content = response.choices[0].message.content
            metadata = json.loads(content)
            logger.info("Metadata generated successfully.")
            return metadata

        except Exception as e:
            logger.error(f"Failed to generate metadata: {e}")
            raise

    def generate_art(self, prompt):
        """
        Generate album art using DALL-E 3.

        Args:
            prompt (str): Description for the image.

        Returns:
            str: URL of the generated image.
        """
        try:
            logger.info(f"Generating album art for prompt: '{prompt}'...")
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            logger.info(f"Album art generated: {image_url}")
            return image_url

        except Exception as e:
            logger.error(f"Failed to generate art: {e}")
            raise

if __name__ == "__main__":
    if os.environ.get("OPENAI_API_KEY"):
        generator = ContentGenerator()
        # Test metadata
        import sys
        if len(sys.argv) > 1:
            hymn = sys.argv[1]
            print(generator.generate_metadata(hymn))
        else:
            print("Usage: python content_generator.py <hymn_name>")
    else:
        print("OPENAI_API_KEY not set. Skipping real test.")
