"""Tests para scripts/python/find-secrets.py.

Ejecutar:  python -X utf8 -m unittest discover -s tests -v
"""

import importlib.util
import os
import json
import subprocess
import sys
import shutil
import tempfile
import unittest
from unittest import mock
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


    def test_results_hide_secret_values_and_absolute_root(self):
        tmp = tempfile.mkdtemp(prefix="scanner_private_path_")
        try:
            nested = os.path.join(tmp, "src")
            os.makedirs(nested)
            value = "B" * 24
            with open(os.path.join(nested, "app.env"), "w", encoding="utf-8") as fh:
                fh.write("api" + "_key = " + '"' + value + '"' + "\\n")
            findings, scanned = self.mod.scan_directory(tmp)
            self.assertEqual(scanned, 1)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["file"], "src/app.env")
            self.assertEqual(findings[0]["match"], "[REDACTED]")
            self.assertEqual(findings[0]["context"], "[REDACTED]")
            self.assertNotIn(tmp, repr(findings))
            self.assertNotIn(value, repr(findings))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_real_credentials_in_example_and_sample_paths_are_detected(self):
        with tempfile.TemporaryDirectory(prefix="scanner_example_paths_") as tmp:
            for folder in (".examples", ".samples"):
                base = Path(tmp, folder)
                base.mkdir()
                for filename in ("config.example", "config.sample"):
                    value = "F" * 24
                    (base / filename).write_text(
                        "api" + "_key=" + value + "\n", encoding="utf-8"
                    )
            findings, scanned = self.mod.scan_directory(tmp)
            self.assertEqual(scanned, 4)
            self.assertEqual(len(findings), 4)
            self.assertEqual(
                {item["file"] for item in findings},
                {
                    f"{folder}/{filename}"
                    for folder in (".examples", ".samples")
                    for filename in ("config.example", "config.sample")
                },
            )
            self.assertTrue(all(item["match"] == "[REDACTED]" for item in findings))

    def test_excluded_parent_of_scan_root_does_not_hide_project_files(self):
        with tempfile.TemporaryDirectory(prefix="scanner_parent_") as tmp:
            project = Path(tmp, "build", "project")
            project.mkdir(parents=True)
            (project / "app.env").write_text(
                "api" + "_key=" + "G" * 24 + "\n", encoding="utf-8"
            )
            excluded = project / "node_modules"
            excluded.mkdir()
            (excluded / "ignored.env").write_text(
                "api" + "_key=" + "H" * 24 + "\n", encoding="utf-8"
            )
            findings, scanned = self.mod.scan_directory(project)
            self.assertEqual(scanned, 1)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["file"], "app.env")


    def test_directory_walk_errors_are_not_reported_as_clean(self):
        tmp = tempfile.mkdtemp(prefix="scanner_walk_error_")
        try:
            def broken_walk(root, onerror=None):
                self.assertIsNotNone(onerror)
                onerror(PermissionError("Access denied"))
                yield root, [], []

            with mock.patch.object(self.mod.os, "walk", broken_walk):
                with self.assertRaises(OSError):
                    self.mod.scan_directory(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_file_path_is_not_misreported_as_directory_scan(self):
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as f:
            f.write("test")
            f.flush()
            with self.assertRaises(OSError):
                self.mod.scan_directory(f.name)


    def test_cli_json_exit_codes_and_redaction(self):
        with tempfile.TemporaryDirectory(prefix="scanner_cli_") as tmp:
            path = os.path.join(tmp, "config.env")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("nothing sensitive here" + chr(10))

            command = [sys.executable, str(MODULE_PATH), tmp, "--format", "json"]
            clean = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(clean.returncode, 0, clean.stderr)
            self.assertEqual(json.loads(clean.stdout), {"scanned": 1, "findings": []})

            fake_key = "C" * 24
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("api" + "_key=" + fake_key + chr(10))
            found = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(found.returncode, 1, found.stderr)
            payload = json.loads(found.stdout)
            self.assertEqual(payload["scanned"], 1)
            self.assertEqual(payload["findings"][0]["file"], "config.env")
            self.assertNotIn(fake_key, found.stdout)
            self.assertNotIn(tmp, found.stdout)

            os.remove(path)
            empty = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(empty.returncode, 2)
            self.assertEqual(json.loads(empty.stdout), {"scanned": 0, "findings": []})


    def test_invalid_utf8_is_incomplete_not_clean(self):
        with tempfile.TemporaryDirectory(prefix="scanner_bad_utf8_") as tmp:
            Path(tmp, "valid.txt").write_text("ordinary text\n", encoding="utf-8")
            Path(tmp, "invalid.txt").write_bytes(b"token=bad\xffvalue\n")
            with self.assertRaises(OSError):
                self.mod.scan_directory(tmp)

    def test_oversized_file_is_incomplete_not_clean(self):
        with tempfile.TemporaryDirectory(prefix="scanner_large_") as tmp:
            Path(tmp, "valid.txt").write_text("ordinary text\n", encoding="utf-8")
            Path(tmp, "large.txt").write_bytes(b"x" * 1_000_001)
            with self.assertRaises(OSError):
                self.mod.scan_directory(tmp)

    def test_cli_incomplete_scan_exits_two_without_clean_result(self):
        with tempfile.TemporaryDirectory(prefix="scanner_cli_large_") as tmp:
            Path(tmp, "valid.txt").write_text("ordinary text\n", encoding="utf-8")
            Path(tmp, "large.txt").write_bytes(b"x" * 1_000_001)
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), tmp, "--format", "json"],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("incompleto", result.stderr)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unsupported")
    def test_file_symlink_is_rejected_without_reading_external_data(self):
        with tempfile.TemporaryDirectory(prefix="scanner_link_root_") as tmp:
            with tempfile.TemporaryDirectory(prefix="scanner_link_external_") as outside:
                Path(tmp, "valid.txt").write_text("ordinary text\n", encoding="utf-8")
                target = Path(outside, "outside.txt")
                target.write_text("api" + "_key=" + "D" * 24, encoding="utf-8")
                try:
                    os.symlink(target, Path(tmp, "linked.txt"))
                except (OSError, NotImplementedError) as exc:
                    self.skipTest(f"symlinks unavailable: {exc}")
                with self.assertRaises(OSError):
                    self.mod.scan_directory(tmp)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unsupported")
    def test_directory_symlink_is_not_silently_skipped(self):
        with tempfile.TemporaryDirectory(prefix="scanner_link_root_") as tmp:
            with tempfile.TemporaryDirectory(prefix="scanner_link_external_") as outside:
                Path(tmp, "valid.txt").write_text("ordinary text\n", encoding="utf-8")
                Path(outside, "external.txt").write_text("ordinary text\n", encoding="utf-8")
                try:
                    os.symlink(outside, Path(tmp, "linked-dir"), target_is_directory=True)
                except (OSError, NotImplementedError) as exc:
                    self.skipTest(f"symlinks unavailable: {exc}")
                with self.assertRaises(OSError):
                    self.mod.scan_directory(tmp)

if __name__ == "__main__":
    unittest.main()
