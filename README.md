# NLP Political Bias API

This project prepares and explores the FACTOID political corpus for downstream training and API usage.

## Quick start

Install dependencies:

```bash
uv sync
```

Optional: activate the virtual environment:

```bash
source .venv/bin/activate
```

## Corpus workflow

The data pipeline lives in:

- `training/download_corpus.py`
- `training/prepare_corpus.py`

### 1) Download and extract the corpus

```bash
uv run training/download_corpus.py
```

What it does:

- Downloads the corpus from Google Drive.
- Extracts it to pickle format.
- Removes the `.gzip` archive by default after extraction.

Useful options:

```bash
# Re-download and re-extract even if the corpus already exists
uv run training/download_corpus.py --force

# Keep the .gzip archive after extraction
uv run training/download_corpus.py --keep-archive
```

Main output:

- `data/raw/reddit_corpus_unbalanced_filtered.pkl`

### 2) Generate processed dataset(s)

User-level dataset (recommended starting point):

```bash
uv run training/prepare_corpus.py --level user
```

Post-level dataset (one row per post):

```bash
uv run training/prepare_corpus.py --level post
```

Outputs:

- `data/processed/reddit_users_text_label.csv`
- `data/processed/reddit_posts_text_label.csv` (only generated when using `--level post`)

## Shared path module

Filesystem paths are centralized in:

- `src/political_bias_api/core/paths.py`

This keeps paths consistent across:

- training scripts
- notebooks
- app/API code

## Dataset exploration notebook

Primary notebook:

- `notebooks/01_dataset_exploration.ipynb`

The notebook imports shared paths so it works consistently regardless of working directory.

## Version-control note

Large artifacts (`data/raw`, `data/processed`, `models`) are ignored by Git.  
The repository versions pipeline code, not generated datasets.
