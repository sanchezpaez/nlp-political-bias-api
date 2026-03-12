# NLP Political Bias API

This project prepares and explores the FACTOID political corpus for downstream model training and API usage.

## Environment

- Python baseline: `3.11` (project minimum is `>=3.11`)
- Dependency manager: `uv`

Install dependencies:

```bash
uv sync
```

Optional: activate the environment:

```bash
source .venv/bin/activate
```

## Corpus workflow

Pipeline scripts:

- `training/download_corpus.py`
- `training/prepare_corpus.py`

### 1) Download and extract corpus

```bash
uv run training/download_corpus.py
```

What it does:

- Downloads the corpus archive from Google Drive.
- Extracts the archive into pickle format.
- Removes the `.gzip` archive by default after extraction.

Useful options:

```bash
uv run training/download_corpus.py --force
uv run training/download_corpus.py --keep-archive
```

Main output:

- `data/raw/reddit_corpus_unbalanced_filtered.pkl`

### 2) Build processed datasets

User-level dataset:

```bash
uv run training/prepare_corpus.py --level user
```

Post-level dataset (one row per post):

```bash
uv run training/prepare_corpus.py --level post
```

Outputs:

- `data/processed/reddit_users_text_label.csv`
- `data/processed/reddit_posts_text_label.csv` (only when using `--level post`)

## Shared paths

All common filesystem paths are defined in:

- `src/political_bias_api/core/paths.py`

This module is used by scripts and notebooks to avoid path drift.

## Notebooks

### Notebook 1

- `notebooks/01_dataset_exploration.ipynb`
- Full exploratory analysis of user-level processed data (schema, quality checks, label distribution, activity, text length, raw vs processed coverage).

### Notebook 2

- `notebooks/02_semantic_exploration.ipynb`
- Currently implemented sections:
	1. Environment setup and dependencies
	2. User-level loading and schema validation
	3. Analysis dataset assembly using processed data as-is (no duplicated preprocessing)
- Next planned sections:
	4. Programmatic semantic exploration (CountVectorizer + UMAP/embeddings)
	5. Artifact persistence

## Testing

Current unit tests:

- `tests/test_prepare_corpus.py`
- `tests/test_download_corpus.py`

Run all tests:

```bash
uv run pytest -q
```

Run per script:

```bash
uv run pytest -q tests/test_prepare_corpus.py
uv run pytest -q tests/test_download_corpus.py
```

## Version control note

Large generated artifacts (`data/raw`, `data/processed`, `models`) are ignored by Git.
The repository tracks code and reproducible workflows, not generated datasets.
