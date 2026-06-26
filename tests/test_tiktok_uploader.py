import unittest
from unittest.mock import patch, MagicMock
from hymn_remaker.src.social.tiktok_uploader import TikTokUploader

class TestTikTokUploader(unittest.TestCase):
    @patch("os.environ.get")
    def test_is_configured(self, mock_env):
        mock_env.side_effect = lambda k: "mock_value" if k in ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_ACCESS_TOKEN"] else None
        uploader = TikTokUploader()
        self.assertTrue(uploader.is_configured())

        mock_env.side_effect = lambda k: None
        uploader_unconfigured = TikTokUploader()
        self.assertFalse(uploader_unconfigured.is_configured())

    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=1024)
    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data=b"dummy_video_data")
    @patch("requests.post")
    @patch("requests.put")
    @patch.object(TikTokUploader, "is_configured", return_value=True)
    def test_upload_success(self, mock_is_configured, mock_put, mock_post, mock_open, mock_getsize, mock_exists):
        uploader = TikTokUploader()

        # Mock init upload response
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "data": {
                "publish_id": "test_publish_id",
                "upload_url": "http://test-upload.url"
            }
        }
        mock_post.return_value = mock_post_response

        # Mock video upload response
        mock_put_response = MagicMock()
        mock_put.return_value = mock_put_response

        publish_id = uploader.upload("dummy_path.mp4", "Test Title")

        self.assertEqual(publish_id, "test_publish_id")
        mock_post.assert_called_once()
        mock_put.assert_called_once()

if __name__ == "__main__":
    unittest.main()
