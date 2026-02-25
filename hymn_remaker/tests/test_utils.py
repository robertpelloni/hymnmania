import unittest
from unittest.mock import MagicMock
from hymn_remaker.src.utils import retry_request

class TestUtils(unittest.TestCase):
    def test_retry_success(self):
        mock_func = MagicMock(return_value="success")
        mock_func.__name__ = "mock_func"
        decorated = retry_request(max_retries=2, delay=0)(mock_func)

        result = decorated()

        self.assertEqual(result, "success")
        mock_func.assert_called_once()

    def test_retry_fail_then_success(self):
        # Fail twice then succeed
        mock_func = MagicMock(side_effect=[Exception("fail1"), Exception("fail2"), "success"])
        mock_func.__name__ = "mock_func"
        decorated = retry_request(max_retries=2, delay=0)(mock_func)

        result = decorated()

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 3)

    def test_retry_fail_max(self):
        # Fail always
        mock_func = MagicMock(side_effect=Exception("fail"))
        mock_func.__name__ = "mock_func"
        decorated = retry_request(max_retries=2, delay=0)(mock_func)

        with self.assertRaises(Exception):
            decorated()

        # Called once + 2 retries = 3 calls
        self.assertEqual(mock_func.call_count, 3)

if __name__ == '__main__':
    unittest.main()
