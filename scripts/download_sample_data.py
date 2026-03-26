#!/usr/bin/env python3
"""Download sample PDF papers for testing the RAG system.

Usage:
    python scripts/download_sample_data.py
    python scripts/download_sample_data.py --output-dir /path/to/dir
"""

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

SAMPLE_PAPERS = [
    {
        "name": "attention_is_all_you_need.pdf",
        "url": "https://arxiv.org/pdf/1706.03762v7",
        "sha256": None,
        "description": "Vaswani et al. - Attention Is All You Need (2017)",
    },
    {
        "name": "retrieval_augmented_generation.pdf",
        "url": "https://arxiv.org/pdf/2005.11401v4",
        "sha256": None,
        "description": "Lewis et al. - Retrieval-Augmented Generation (2020)",
    },
]

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_papers"


def download_file(url: str, dest: Path, expected_sha256: str | None = None) -> bool:
    """Download a file from a URL to a destination path.

    Args:
        url: Source URL.
        dest: Destination file path.
        expected_sha256: Optional SHA-256 hash to verify the download.

    Returns:
        True if downloaded, False if already exists and is valid.
    """
    if dest.exists():
        if expected_sha256 and _sha256(dest) == expected_sha256:
            return False
        if not expected_sha256:
            return False

    dest.parent.mkdir(parents=True, exist_ok=True)

    print(f"  Downloading: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
    except Exception as e:
        print(f"  ERROR: Failed to download {url}: {e}")
        return False

    dest.write_bytes(data)

    if expected_sha256:
        actual = _sha256(dest)
        if actual != expected_sha256:
            print(f"  WARNING: Hash mismatch for {dest.name}")
            print(f"    Expected: {expected_sha256}")
            print(f"    Got:      {actual}")

    return True


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Download sample papers for RAG testing.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save papers (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading sample papers to: {output_dir}\n")

    downloaded = 0
    skipped = 0

    for paper in SAMPLE_PAPERS:
        dest = output_dir / paper["name"]
        print(f"[{paper['description']}]")

        if download_file(paper["url"], dest, paper["sha256"]):
            size_mb = dest.stat().st_size / (1024 * 1024)
            print(f"  Saved: {dest.name} ({size_mb:.1f} MB)\n")
            downloaded += 1
        else:
            print(f"  Already exists: {dest.name} (skipped)\n")
            skipped += 1

    print(f"Done: {downloaded} downloaded, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
