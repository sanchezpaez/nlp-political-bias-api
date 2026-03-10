"""Download and extract the FACTOID corpus from Google Drive.

This script keeps only one extracted corpus file in ``data/raw`` by default.
The downloaded ``.gzip`` archive is removed after extraction unless
``--keep-archive`` is explicitly provided.
"""

import argparse
import gzip
import shutil
from pathlib import Path

import gdown

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_URL = "https://drive.google.com/uc?id=1pevK3uZVLadH8a5KzT7d1Mlkkjby23Og"
ARCHIVE_PATH = RAW_DIR / "reddit_corpus_unbalanced_filtered.gzip"
EXTRACTED_PATH = RAW_DIR / "reddit_corpus_unbalanced_filtered.pkl"


def download_archive(url: str, output: Path) -> Path:
    """Download the compressed corpus archive from Google Drive."""
    print(f"Downloading corpus archive to: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    downloaded = gdown.download(
        url=url,
        output=str(output),
        quiet=False,
        fuzzy=True,
    )
    if not downloaded:
        raise RuntimeError("Failed to download corpus archive. Check URL and Drive permissions.")

    return Path(downloaded)


def extract_archive(archive_path: Path, extracted_path: Path) -> Path:
    """Extract a gzip archive into a pickle file path."""
    print(f"Extracting archive to: {extracted_path}")
    extracted_path.parent.mkdir(parents=True, exist_ok=True)

    with gzip.open(archive_path, "rb") as source, extracted_path.open("wb") as target:
        shutil.copyfileobj(source, target)

    return extracted_path


def download_and_extract(url: str, keep_archive: bool, force: bool) -> None:
    """Download and extract the corpus, keeping a single extracted file.

    If the extracted corpus already exists and ``force`` is not enabled,
    the function exits without downloading.
    """
    if EXTRACTED_PATH.exists() and not force:
        print(f"Extracted corpus already exists: {EXTRACTED_PATH}")
        print("Use --force to download and extract again.")
        return

    if EXTRACTED_PATH.exists() and force:
        EXTRACTED_PATH.unlink()

    archive = download_archive(url=url, output=ARCHIVE_PATH)
    extracted = extract_archive(archive_path=archive, extracted_path=EXTRACTED_PATH)

    if not keep_archive and archive.exists():
        archive.unlink()
        print(f"Removed archive: {archive}")

    print(f"Corpus ready at: {extracted}")


def main() -> None:
    """Parse CLI arguments and execute corpus download workflow."""
    parser = argparse.ArgumentParser(description="Download and extract FACTOID corpus")
    parser.add_argument("--url", default=DEFAULT_URL, help="Google Drive file URL or ID")
    parser.add_argument(
        "--keep-archive",
        action="store_true",
        help="Keep .gzip archive after extraction (default removes it)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download again even if extracted corpus already exists",
    )
    args = parser.parse_args()

    download_and_extract(url=args.url, keep_archive=args.keep_archive, force=args.force)


if __name__ == "__main__":
    main()