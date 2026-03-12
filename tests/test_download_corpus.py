"""Unit tests for training/download_corpus.py.

These tests validate each core step independently:
1) extraction from gzip,
2) download error handling,
3) orchestration behavior with force/keep flags.
"""

import gzip
from pathlib import Path

import pytest


def test_extract_archive_writes_expected_bytes(tmp_path, download_module):
	"""`extract_archive` should copy gzip payload bytes to the pickle output file."""
	archive_path = tmp_path / "corpus.gzip"
	extracted_path = tmp_path / "corpus.pkl"
	payload = b"payload-bytes"

	with gzip.open(archive_path, "wb") as file:
		file.write(payload)

	output = download_module.extract_archive(archive_path=archive_path, extracted_path=extracted_path)

	assert output == extracted_path
	assert extracted_path.read_bytes() == payload


def test_download_archive_raises_when_gdown_returns_none(tmp_path, download_module, monkeypatch):
	"""`download_archive` should raise RuntimeError when gdown reports a failed download."""
	output_path = tmp_path / "archive.gzip"

	class FakeGdown:
		@staticmethod
		def download(**kwargs):
			return None

	monkeypatch.setattr(download_module, "gdown", FakeGdown)

	with pytest.raises(RuntimeError, match="Failed to download corpus archive"):
		download_module.download_archive(url="https://example.com", output=output_path)


def test_download_and_extract_skips_when_extracted_exists(tmp_path, download_module, monkeypatch):
	"""If extracted corpus already exists and force=False, workflow should skip download."""
	extracted_path = tmp_path / "existing.pkl"
	extracted_path.write_text("already-there")

	monkeypatch.setattr(download_module, "EXTRACTED_PATH", extracted_path)
	monkeypatch.setattr(download_module, "ARCHIVE_PATH", tmp_path / "archive.gzip")
	monkeypatch.setattr(download_module, "ensure_data_dirs", lambda: None)

	def _unexpected(*args, **kwargs):
		raise AssertionError("download_archive should not be called when extracted file exists")

	monkeypatch.setattr(download_module, "download_archive", _unexpected)

	result = download_module.download_and_extract(
		url="https://example.com",
		keep_archive=False,
		force=False,
	)

	assert result is None
	assert extracted_path.read_text() == "already-there"


def test_download_and_extract_force_overwrites_and_removes_archive(tmp_path, download_module, monkeypatch):
	"""With force=True and keep_archive=False, workflow should overwrite output and delete archive."""
	archive_path = tmp_path / "archive.gzip"
	extracted_path = tmp_path / "corpus.pkl"
	extracted_path.write_text("old")

	monkeypatch.setattr(download_module, "ARCHIVE_PATH", archive_path)
	monkeypatch.setattr(download_module, "EXTRACTED_PATH", extracted_path)
	monkeypatch.setattr(download_module, "ensure_data_dirs", lambda: None)

	def _fake_download_archive(url: str, output: Path) -> Path:
		with gzip.open(output, "wb") as file:
			file.write(b"fresh-bytes")
		return output

	monkeypatch.setattr(download_module, "download_archive", _fake_download_archive)

	result = download_module.download_and_extract(
		url="https://example.com",
		keep_archive=False,
		force=True,
	)

	assert result is None
	assert extracted_path.read_bytes() == b"fresh-bytes"
	assert not archive_path.exists()


def test_download_and_extract_keeps_archive_when_requested(tmp_path, download_module, monkeypatch):
	"""With keep_archive=True, workflow should keep the downloaded gzip file."""
	archive_path = tmp_path / "archive.gzip"
	extracted_path = tmp_path / "corpus.pkl"

	monkeypatch.setattr(download_module, "ARCHIVE_PATH", archive_path)
	monkeypatch.setattr(download_module, "EXTRACTED_PATH", extracted_path)
	monkeypatch.setattr(download_module, "ensure_data_dirs", lambda: None)

	def _fake_download_archive(url: str, output: Path) -> Path:
		with gzip.open(output, "wb") as file:
			file.write(b"keep-archive")
		return output

	monkeypatch.setattr(download_module, "download_archive", _fake_download_archive)

	result = download_module.download_and_extract(
		url="https://example.com",
		keep_archive=True,
		force=False,
	)

	assert result is None
	assert archive_path.exists()
	assert extracted_path.read_bytes() == b"keep-archive"
