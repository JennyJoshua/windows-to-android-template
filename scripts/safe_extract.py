#!/usr/bin/env python3
"""Safely validate and extract untrusted ZIP archives."""

import argparse
import json
import re
import shutil
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

MAX_ARCHIVE_SIZE = 200 * 1024 * 1024
MAX_FILES = 10000
MAX_TOTAL_SIZE = 1024 * 1024 * 1024
MAX_FILE_SIZE = 200 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200


class UnsafeArchiveError(Exception):
    """Raised when an archive fails security validation."""


def validate_archive(archive):
    if not archive.is_file():
        raise UnsafeArchiveError("Input archive does not exist.")

    if archive.stat().st_size > MAX_ARCHIVE_SIZE:
        raise UnsafeArchiveError("Archive exceeds the 200 MB limit.")

    entries = []
    seen = set()
    total_size = 0
    file_count = 0

    try:
        with zipfile.ZipFile(archive, "r") as zf:
            members = zf.infolist()

            if len(members) > MAX_FILES:
                raise UnsafeArchiveError(
                    "Archive contains too many entries."
                )

            for member in members:
                raw_name = member.filename

                if not raw_name or "\x00" in raw_name:
                    raise UnsafeArchiveError(
                        "Archive contains an invalid filename."
                    )

                if "\\" in raw_name:
                    raise UnsafeArchiveError(
                        "Backslashes in archive paths are not allowed."
                    )

                if raw_name.startswith("/") or raw_name.startswith("//"):
                    raise UnsafeArchiveError(
                        "Absolute paths are not allowed."
                    )

                if re.match(r"^[A-Za-z]:", raw_name):
                    raise UnsafeArchiveError(
                        "Windows drive paths are not allowed."
                    )

                path = PurePosixPath(raw_name)
                parts = raw_name.rstrip("/").split("/")

                if any(part in ("", ".", "..") for part in parts):
                    raise UnsafeArchiveError(
                        "Unsafe or ambiguous archive path."
                    )

                if path.is_absolute():
                    raise UnsafeArchiveError(
                        "Absolute paths are not allowed."
                    )

                if any(":" in part for part in parts):
                    raise UnsafeArchiveError(
                        "Colon characters in paths are not allowed."
                    )

                normalized = path.as_posix().casefold()

                if normalized in seen:
                    raise UnsafeArchiveError(
                        "Duplicate or case-colliding archive path."
                    )

                seen.add(normalized)

                mode = member.external_attr >> 16
                file_type = stat.S_IFMT(mode)

                if file_type == stat.S_IFLNK:
                    raise UnsafeArchiveError(
                        "Symbolic links are not allowed."
                    )

                is_directory = member.is_dir()

                if file_type not in (
                    0,
                    stat.S_IFREG,
                    stat.S_IFDIR,
                ):
                    raise UnsafeArchiveError(
                        "Special files are not allowed."
                    )

                if is_directory:
                    if file_type == stat.S_IFREG:
                        raise UnsafeArchiveError(
                            "Inconsistent directory entry."
                        )
                else:
                    if file_type == stat.S_IFDIR:
                        raise UnsafeArchiveError(
                            "Inconsistent file entry."
                        )

                    file_count += 1
                    total_size += member.file_size

                    if member.file_size > MAX_FILE_SIZE:
                        raise UnsafeArchiveError(
                            "A file exceeds the 200 MB limit."
                        )

                    if total_size > MAX_TOTAL_SIZE:
                        raise UnsafeArchiveError(
                            "Extracted content exceeds the 1 GB limit."
                        )

                    if member.file_size > 0:
                        if member.compress_size == 0:
                            raise UnsafeArchiveError(
                                "Invalid compression size."
                            )

                        ratio = (
                            member.file_size / member.compress_size
                        )

                        if ratio > MAX_COMPRESSION_RATIO:
                            raise UnsafeArchiveError(
                                "Suspicious compression ratio."
                            )

                entries.append(member)

            if file_count == 0:
                raise UnsafeArchiveError(
                    "Archive contains no regular files."
                )

            return entries, file_count, total_size

    except zipfile.BadZipFile as exc:
        raise UnsafeArchiveError("Invalid or corrupted ZIP archive.") from exc


def safe_extract(archive, destination):
    archive = Path(archive)
    destination = Path(destination)

    if destination.exists():
        raise UnsafeArchiveError(
            "Destination already exists. Refusing to overwrite it."
        )

    entries, file_count, total_size = validate_archive(archive)

    destination.mkdir(parents=True, exist_ok=False)

    try:
        with zipfile.ZipFile(archive, "r") as zf:
            for member in entries:
                target = destination.joinpath(*member.filename.split("/"))

                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue

                target.parent.mkdir(parents=True, exist_ok=True)

                # Exclusive creation prevents overwriting existing files.
                with zf.open(member, "r") as source:
                    with target.open("xb") as output:
                        shutil.copyfileobj(source, output)

                if target.stat().st_size != member.file_size:
                    raise UnsafeArchiveError(
                        "Extracted file size does not match the archive."
                    )

        # Verify CRC values for all entries.
        with zipfile.ZipFile(archive, "r") as zf:
            bad_member = zf.testzip()

        if bad_member is not None:
            raise UnsafeArchiveError(
                f"Archive integrity check failed: {bad_member}"
            )

    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise

    return {
        "status": "success",
        "archive": archive.name,
        "files_extracted": file_count,
        "uncompressed_bytes": total_size,
        "destination": str(destination),
        "code_executed": False,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate and safely extract a ZIP archive."
    )
    parser.add_argument("archive", help="Path to the input ZIP archive")
    parser.add_argument("destination", help="New extraction directory")
    parser.add_argument(
        "--report",
        help="Optional JSON report output path",
    )
    args = parser.parse_args()

    try:
        result = safe_extract(args.archive, args.destination)
        print(json.dumps(result, indent=2))

        if args.report:
            Path(args.report).parent.mkdir(
                parents=True, exist_ok=True
            )
            Path(args.report).write_text(
                json.dumps(result, indent=2),
                encoding="utf-8",
            )

    except (
        UnsafeArchiveError,
        OSError,
        zipfile.BadZipFile,
        RuntimeError,
    ) as exc:
        result = {
            "status": "failed",
            "error": str(exc),
            "code_executed": False,
        }

        print(json.dumps(result, indent=2), file=sys.stderr)

        if args.report:
            report_path = Path(args.report)
            report_path.parent.mkdir(
                parents=True, exist_ok=True
            )
            report_path.write_text(
                json.dumps(result, indent=2),
                encoding="utf-8",
            )

        sys.exit(1)


if __name__ == "__main__":
    main()
