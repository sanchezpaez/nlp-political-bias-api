"""Prepare train-ready CSV datasets from the extracted FACTOID corpus."""

import argparse
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from political_bias_api.core.paths import CORPUS_PKL, POSTS_CSV, USERS_CSV, ensure_data_dirs

RAW_CORPUS_PATH = CORPUS_PKL


def _safe_text(value: Any) -> str:
    """Convert values to stripped strings, preserving empty values as empty text."""
    if value is None:
        return ""
    return str(value).strip()


def _parse_document(document: Any) -> Optional[Dict[str, str]]:
    """Parse one document tuple into a normalized dictionary.

    Expected tuple schema is approximately:
    ``(doc_id, text, created_at, subreddit, ...)``
    """
    if not isinstance(document, (list, tuple)) or len(document) < 2:
        return None

    text = _safe_text(document[1])
    if not text:
        return None

    return {
        "doc_id": _safe_text(document[0]),
        "text": text,
        "created_at": _safe_text(document[2]) if len(document) > 2 else "",
        "subreddit": _safe_text(document[3]) if len(document) > 3 else "",
    }


def _validate_columns(dataframe: pd.DataFrame) -> None:
    """Validate minimum columns required to build output datasets."""
    required_columns = {"user_id", "fake_news_spreader", "documents"}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required corpus columns: {missing}")


def _resolve_input_path(input_path: Path) -> Path:
    """Resolve corpus input path and ensure it exists."""
    if input_path.exists():
        return input_path

    raise FileNotFoundError(f"Corpus file not found: {input_path}")


def _iter_parsed_documents(documents: Any) -> Iterable[Dict[str, str]]:
    """Yield parsed document dictionaries from a row-level document list."""
    if not isinstance(documents, list):
        return []

    parsed_documents: List[Dict[str, str]] = []
    for document in documents:
        parsed = _parse_document(document)
        if parsed is not None:
            parsed_documents.append(parsed)
    return parsed_documents


def build_user_level_dataset(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build a user-level dataset where each row contains all user posts merged."""
    records: List[Dict[str, Any]] = []

    for row in dataframe.itertuples(index=False):
        parsed_documents = list(_iter_parsed_documents(row.documents))
        if not parsed_documents:
            continue

        records.append(
            {
                "user_id": row.user_id,
                "label": int(row.fake_news_spreader),
                "n_posts": len(parsed_documents),
                "text": "\n".join(doc["text"] for doc in parsed_documents),
            }
        )

    return pd.DataFrame(records, columns=["user_id", "label", "n_posts", "text"])


def build_post_level_dataset(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build a post-level dataset where each row is one post/document."""
    records: List[Dict[str, Any]] = []

    for row in dataframe.itertuples(index=False):
        parsed_documents = _iter_parsed_documents(row.documents)
        for doc in parsed_documents:
            records.append(
                {
                    "user_id": row.user_id,
                    "doc_id": doc["doc_id"],
                    "created_at": doc["created_at"],
                    "subreddit": doc["subreddit"],
                    "label": int(row.fake_news_spreader),
                    "text": doc["text"],
                }
            )

    return pd.DataFrame(
        records,
        columns=["user_id", "doc_id", "created_at", "subreddit", "label", "text"],
    )


def prepare_dataset(input_path: Path, output_path: Path, level: str) -> None:
    """Load corpus, transform it, and write the resulting CSV.

    Steps:
    1. Resolve and validate input path.
    2. Load pickled DataFrame.
    3. Validate required columns.
    4. Build user-level or post-level output.
    5. Save CSV and print summary stats.
    """
    input_path = _resolve_input_path(input_path)
    ensure_data_dirs()
    print(f"Loading corpus from: {input_path}")
    dataframe = pd.read_pickle(input_path)
    _validate_columns(dataframe)

    if level == "user":
        processed = build_user_level_dataset(dataframe)
    else:
        processed = build_post_level_dataset(dataframe)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output_path, index=False)

    print(f"Dataset written to: {output_path}")
    print(f"Rows: {len(processed)}")
    if "label" in processed.columns:
        print("Label distribution:")
        print(processed["label"].value_counts(dropna=False).to_string())


def main() -> None:
    """Parse CLI arguments and run dataset preparation."""
    parser = argparse.ArgumentParser(
        description="Convert FACTOID pickle corpus into train-ready CSV"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=RAW_CORPUS_PATH,
        help="Path to extracted corpus pickle",
    )
    parser.add_argument(
        "--level",
        choices=["user", "post"],
        default="user",
        help="Output dataset granularity",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Custom output CSV path",
    )
    args = parser.parse_args()

    if args.output is None:
        output_path = USERS_CSV if args.level == "user" else POSTS_CSV
    else:
        output_path = args.output

    prepare_dataset(input_path=args.input, output_path=output_path, level=args.level)


if __name__ == "__main__":
    main()