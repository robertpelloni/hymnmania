import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hymn_remaker.src.content_generator import ContentGenerator

class TestContentGenerator(unittest.TestCase):
    def test_missing_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            gen = ContentGenerator()
            self.assertIsNone(gen.api_key)

    @patch('hymn_remaker.src.content_generator.openai.OpenAI')
    def test_generate_metadata(self, MockOpenAI):
        # Setup mock client
        mock_client = MockOpenAI.return_value

        # Mock chat.completions.create
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "title": "Test Title",
            "description": "Test Desc",
            "tags": ["tag1", "tag2"]
        })
        mock_client.chat.completions.create.return_value = mock_response

        gen = ContentGenerator(api_key="dummy_key")
        metadata = gen.generate_metadata("Test Hymn", "Rock")

        self.assertEqual(metadata["title"], "Test Title")
        self.assertEqual(metadata["description"], "Test Desc")
        self.assertEqual(metadata["tags"], ["tag1", "tag2"])

        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4-turbo")
        self.assertEqual(call_args["response_format"], { "type": "json_object" })

    @patch('hymn_remaker.src.content_generator.openai.OpenAI')
    def test_generate_art(self, MockOpenAI):
        mock_client = MockOpenAI.return_value

        mock_response = MagicMock()
        mock_response.data[0].url = "http://image.url"
        mock_client.images.generate.return_value = mock_response

        gen = ContentGenerator(api_key="dummy_key")
        url = gen.generate_art("A beautiful painting")

        self.assertEqual(url, "http://image.url")
        mock_client.images.generate.assert_called_once()
        call_args = mock_client.images.generate.call_args[1]
        self.assertEqual(call_args["model"], "dall-e-3")

if __name__ == '__main__':
    unittest.main()
