"""Centralized filesystem paths shared across scripts, notebooks, and app code."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = PROJECT_ROOT / "src"

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

CORPUS_PKL = RAW_DIR / "reddit_corpus_unbalanced_filtered.pkl"
USERS_CSV = PROCESSED_DIR / "reddit_users_text_label.csv"
POSTS_CSV = PROCESSED_DIR / "reddit_posts_text_label.csv"


def ensure_data_dirs() -> None:
    """Ensure expected data directories exist."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
