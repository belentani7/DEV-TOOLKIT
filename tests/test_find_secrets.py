"""Tests para scripts/python/find-secrets.py.

Ejecutar:  python -X utf8 -m unittest discover -s tests -v
"""

import importlib.util
import io
import json
import contextlib
import os
import subprocess
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO / "scripts" / "python" / "find-secrets.py"


def load_module():
    spec = importlib.util.spec_from_file_location("find_secrets", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExcludeFilesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_should_exclude_declared_extensions(self):
        # EXCLUDE_FILES documenta "*.png", "*.pyc", "*.so", "*.zip"...
        # Deben excluirse aunque vayan en cualquier ruta.
        for path in ("x/logo.png", "x/mod.pyc", "x/lib.so", "x/backup.zip",
                     "x/font.woff2", "x/archive.7z"):
            with self.subTest(path=path):
                self.assertTrue(self.mod.should_exclude(path),
                                "%s consta en EXCLUDE_FILES y no se excluye" % path)

    def test_should_keep_regular_text_files(self):
        for path in ("x/main.py", "x/README.md", "x/.env", "x/config.json"):
            with self.subTest(path=path):
                self.assertFalse(self.mod.should_exclude(path))

    def test_scan_directory_skips_excluded_extensions(self):
        tmp = tempfile.mkdtemp(prefix="find_secrets_test_")
        try:
            # Construido por concatenacion para que este propio test no
            # sea detectado como falso positivo al escanear el repo.
            fake_key = "A" * 24
            blob = "api" + "_key = \"" + fake_key + "\"\n"
            # Mismo contenido en un .txt (no debe reportarse) y en un .png (no escanearse).
            with open(os.path.join(tmp, "notes.txt"), "w", encoding="utf-8") as f:
                f.write("sin nada aqui\n")
            with open(os.path.join(tmp, "logo.png"), "w", encoding="utf-8") as f:
                f.write(blob)

            findings, scanned = self.mod.scan_directory(tmp)

            self.assertEqual(scanned, 1,
                             "solo debe escanearse notes.txt, logo.png esta en EXCLUDE_FILES")
            self.assertEqual(findings, [],
                             "no debe haber findings en ficheros excluidos")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


    def test_scan_directory_still_detects_text_file(self):
        # Control positivo: la exclusion no debe apagar la deteccion.
        tmp = tempfile.mkdtemp(prefix="find_secrets_test_")
        try:
            fake_key = "A" * 24
            blob = "api" + "_key = \"" + fake_key + "\"\n"
            with open(os.path.join(tmp, "app.txt"), "w", encoding="utf-8") as f:
                f.write(blob)

            findings, scanned = self.mod.scan_directory(tmp)

            self.assertEqual(scanned, 1)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["type"], "API Key (generic)")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


    def test_secret_values_never_reach_findings_or_cli_output(self):
        tmp = tempfile.mkdtemp(prefix="find_secrets_redaction_")
        try:
            fake_value = "A" * 25
            secret_text = "api" + "_key = \"" + fake_value + "\"\n"
            Path(tmp, "creds.txt").write_text(secret_text, encoding="utf-8")
            findings, scanned = self.mod.scan_directory(tmp)
            self.assertEqual(scanned, 1)
            self.assertGreaterEqual(len(findings), 1)
            self.assertEqual(set(findings[0]), {"file", "line", "type"})
            self.assertNotIn(fake_value, repr(findings))

            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                self.mod.print_findings(findings, "text")
            self.assertNotIn(fake_value, stream.getvalue())

            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), tmp, "--format", "json"],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(result.returncode, 1)
            parsed = json.loads(result.stdout)
            self.assertEqual(parsed[0]["type"], "API Key (generic)")
            self.assertNotIn(fake_value, result.stdout)
            self.assertNotIn("context", parsed[0])
            self.assertNotIn("match", parsed[0])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
