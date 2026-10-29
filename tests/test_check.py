import unittest
from unittest.mock import Mock, MagicMock, patch
import json
import tempfile
from pathlib import Path
from scripts import check as checker
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
        response = MagicMock()
        response.status = 200
        response.__enter__.return_value = response
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

class SchedulerGateTests(unittest.TestCase):
    def test_disabled_never_sends_requests(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "monitors.json").write_text(json.dumps([{"name": "Example", "url": "https://example.onrender.com"}]))
            (root / "keepalive.json").write_text('{"enabled": false}')
            with patch.object(checker, "ROOT", root), patch.object(checker, "check") as ping:
                checker.main()
                ping.assert_not_called()
            self.assertFalse((root / "status.json").exists())

    def test_enabled_runs_and_records_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "monitors.json").write_text(json.dumps([{"name": "Example", "url": "https://example.onrender.com"}]))
            (root / "keepalive.json").write_text('{"enabled": true}')
            mock_result = {"name": "Example", "url": "https://example.onrender.com", "status": "online", "latencyMs": 12}
            with patch.object(checker, "ROOT", root), patch.object(checker, "check", return_value=mock_result) as ping:
                checker.main()
                ping.assert_called_once()
            snapshot = json.loads((root / "status.json").read_text())
            self.assertEqual(snapshot["services"][0]["status"], "online")
            self.assertEqual(len(snapshot["history"]), 1)

if __name__ == "__main__":
    unittest.main()
