"""Prevent scanner output from leaking the very credentials it detects."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "python" / "find-secrets.py"


class RedactedScannerTests(unittest.TestCase):
    def test_scanner_does_not_return_secret_value_or_line(self):
        spec = importlib.util.spec_from_file_location("find_secrets_redaction", MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "config.txt"
            marker = "ABCDE" * 8
            file.write_text('api' + '_key="' + marker + '"', encoding="utf-8")
            findings = module.scan_file(str(file))
        self.assertTrue(findings)
        exported = json.dumps(findings)
        self.assertNotIn(marker, exported)
        self.assertEqual(findings[0]["match"], "[REDACTED]")
        self.assertEqual(findings[0]["context"], "[REDACTED]")
        self.assertEqual(findings[0]["line"], 1)


if __name__ == "__main__":
    unittest.main()
