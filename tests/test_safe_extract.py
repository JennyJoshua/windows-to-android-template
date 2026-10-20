import sys
import stat
import tempfile
import unittest
import zipfile

from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "scripts"),
)

from safe_extract import safe_extract, UnsafeArchiveError


class SafeExtractTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.archive = self.root / "input.zip"
        self.destination = self.root / "extracted"

    def tearDown(self):
        self.temp.cleanup()

    def make_zip(self, entries):
        with zipfile.ZipFile(
            self.archive, "w", zipfile.ZIP_DEFLATED
        ) as zf:
            for name, content in entries:
                zf.writestr(name, content)

    def test_extracts_valid_archive(self):
        self.make_zip([
            ("README.md", "Test project"),
            ("src/main.txt", "Sample source"),
        ])

        result = safe_extract(self.archive, self.destination)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["files_extracted"], 2)
        self.assertEqual(
            (self.destination / "README.md").read_text(),
            "Test project",
        )
        self.assertFalse(result["code_executed"])

    def test_rejects_path_traversal(self):
        self.make_zip([("../outside.txt", "unsafe")])

        with self.assertRaises(UnsafeArchiveError):
            safe_extract(self.archive, self.destination)

        self.assertFalse((self.root.parent / "outside.txt").exists())
        self.assertFalse(self.destination.exists())

    def test_rejects_absolute_path(self):
        self.make_zip([("/tmp/outside.txt", "unsafe")])

        with self.assertRaises(UnsafeArchiveError):
            safe_extract(self.archive, self.destination)

        self.assertFalse(self.destination.exists())

    def test_rejects_backslash_paths(self):
        self.make_zip([("folder\\unsafe.txt", "unsafe")])

        with self.assertRaises(UnsafeArchiveError):
            safe_extract(self.archive, self.destination)

    def test_rejects_case_colliding_paths(self):
        self.make_zip([
            ("Readme.txt", "first"),
            ("README.TXT", "second"),
        ])

        with self.assertRaises(UnsafeArchiveError):
            safe_extract(self.archive, self.destination)

    def test_rejects_symbolic_links(self):
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16

        with zipfile.ZipFile(self.archive, "w") as zf:
            zf.writestr(info, "target.txt")

        with self.assertRaises(UnsafeArchiveError):
            safe_extract(self.archive, self.destination)

    def test_refuses_existing_destination(self):
        self.make_zip([("file.txt", "new content")])
        self.destination.mkdir()
        existing_file = self.destination / "existing.txt"
        existing_file.write_text("keep this")

        with self.assertRaises(UnsafeArchiveError):
            safe_extract(self.archive, self.destination)

        self.assertEqual(existing_file.read_text(), "keep this")

    def test_rejects_corrupted_archive(self):
        self.archive.write_bytes(b"not a valid ZIP archive")

        with self.assertRaises(UnsafeArchiveError):
            safe_extract(self.archive, self.destination)

        self.assertFalse(self.destination.exists())

    def test_rejects_archive_without_regular_files(self):
        with zipfile.ZipFile(self.archive, "w") as zf:
            zf.writestr("empty-folder/", "")

        with self.assertRaises(UnsafeArchiveError):
            safe_extract(self.archive, self.destination)

    def test_enforces_individual_file_size_limit(self):
        self.make_zip([("large.txt", "12345")])

        with patch("safe_extract.MAX_FILE_SIZE", 4):
            with self.assertRaises(UnsafeArchiveError):
                safe_extract(self.archive, self.destination)

        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
