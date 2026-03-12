"""Unit tests for training/prepare_corpus.py.

The goal is to validate text normalization, row parsing, dataset building,
and end-to-end CSV generation behavior.
"""

import pandas as pd
import pytest


def test_safe_text_normalization(prepare_module):
	"""`_safe_text` should normalize None, strip strings, and cast non-strings."""
	assert prepare_module._safe_text(None) == ""
	assert prepare_module._safe_text("  hello  ") == "hello"
	assert prepare_module._safe_text(123) == "123"


def test_parse_document_filters_invalid_rows(prepare_module):
	"""`_parse_document` should reject invalid documents and parse valid tuples."""
	assert prepare_module._parse_document("not-a-doc") is None
	assert prepare_module._parse_document(("d1", "   ")) is None

	parsed = prepare_module._parse_document(("d1", " text ", "2020", "python"))
	assert parsed == {
		"doc_id": "d1",
		"text": "text",
		"created_at": "2020",
		"subreddit": "python",
	}


def test_validate_columns_raises_for_missing(prepare_module):
	"""`_validate_columns` should fail when required corpus columns are missing."""
	dataframe = pd.DataFrame({"user_id": ["u1"]})
	with pytest.raises(ValueError, match="Missing required corpus columns"):
		prepare_module._validate_columns(dataframe)


def test_build_user_level_dataset(prepare_module):
	"""`build_user_level_dataset` should aggregate valid posts per user."""
	dataframe = pd.DataFrame(
		{
			"user_id": ["u1", "u2"],
			"fake_news_spreader": [1, 0],
			"documents": [
				[("d1", "first post", "2020", "a"), ("d2", "second post", "2021", "b")],
				[("x", "   ")],
			],
		}
	)

	output = prepare_module.build_user_level_dataset(dataframe)
	assert list(output.columns) == ["user_id", "label", "n_posts", "text"]
	assert len(output) == 1
	assert output.iloc[0]["user_id"] == "u1"
	assert output.iloc[0]["label"] == 1
	assert output.iloc[0]["n_posts"] == 2
	assert output.iloc[0]["text"] == "first post\nsecond post"


def test_build_post_level_dataset(prepare_module):
	"""`build_post_level_dataset` should output one row per parsed document."""
	dataframe = pd.DataFrame(
		{
			"user_id": ["u1"],
			"fake_news_spreader": [0],
			"documents": [[("d1", "first", "2020", "python"), ("d2", "second", "2021", "ml")]],
		}
	)

	output = prepare_module.build_post_level_dataset(dataframe)
	assert list(output.columns) == ["user_id", "doc_id", "created_at", "subreddit", "label", "text"]
	assert len(output) == 2
	assert set(output["doc_id"].tolist()) == {"d1", "d2"}


def test_prepare_dataset_writes_user_csv(tmp_path, prepare_module, monkeypatch):
	"""`prepare_dataset` should write a user-level CSV with expected schema and values."""
	dataframe = pd.DataFrame(
		{
			"user_id": ["u1"],
			"fake_news_spreader": [1],
			"documents": [[("d1", "hello world", "2020", "nlp")]],
		}
	)

	input_path = tmp_path / "corpus.pkl"
	output_path = tmp_path / "users.csv"
	dataframe.to_pickle(input_path)

	monkeypatch.setattr(prepare_module, "ensure_data_dirs", lambda: None)
	prepare_module.prepare_dataset(input_path=input_path, output_path=output_path, level="user")

	saved = pd.read_csv(output_path)
	assert list(saved.columns) == ["user_id", "label", "n_posts", "text"]
	assert len(saved) == 1
	assert saved.iloc[0]["n_posts"] == 1
	assert saved.iloc[0]["text"] == "hello world"


def test_prepare_dataset_missing_input_raises(tmp_path, prepare_module):
	"""`prepare_dataset` should raise when the input pickle file does not exist."""
	missing_input = tmp_path / "missing.pkl"
	output_path = tmp_path / "users.csv"
	with pytest.raises(FileNotFoundError):
		prepare_module.prepare_dataset(input_path=missing_input, output_path=output_path, level="user")
