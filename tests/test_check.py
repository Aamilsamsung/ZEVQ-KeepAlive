import unittest
from unittest.mock import Mock
from scripts.check import validate_url, check

class ValidationTests(unittest.TestCase):
    def test_allowed(self):
        self.assertTrue(validate_url("https://example.onrender.com/health"))
    def test_rejects_internal_and_unsafe(self):
        for url in ("http://example.onrender.com", "https://127.0.0.1/",
                    "https://example.onrender.com.evil.test/",
                    "https://user:pass@example.onrender.com/",
                    "https://example.onrender.com:444/",
                    "https://example.onrender.com/#token",
                    "https://example.onrender.com:bad/"):
            with self.subTest(url=url):
                self.assertFalse(validate_url(url))
    def test_online(self):
        response = Mock()
        response.status = 200
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=None)
        opener = Mock()
        opener.open.return_value = response
        result = check({"name": "Example", "url": "https://example.onrender.com"}, opener=opener)
        self.assertEqual(result["status"], "online")
        self.assertIsInstance(result["latencyMs"], int)
    def test_invalid_does_not_request(self):
        opener = Mock()
        result = check({"name": "Bad", "url": "https://localhost/"}, opener=opener)
        self.assertEqual(result["status"], "invalid")
        opener.open.assert_not_called()

if __name__ == "__main__":
    unittest.main()
