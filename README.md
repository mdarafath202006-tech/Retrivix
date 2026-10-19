# Retrivix

A small, inspectable full-text search engine in Python. It implements document ingestion, tokenization, an inverted index, BM25 ranking, JSON persistence, and a CLI without external dependencies.

**Browser preview:** [retrivix-mdarafath202006.vercel.app](https://retrivix-mdarafath202006.vercel.app/). The hosted page is a standalone UI demonstration; it does not call the Python CLI or search engine.

## Requirements
- Python 3.10+
- No third-party packages

## Quick start
```bash
python retrivix.py index examples
python retrivix.py search "inverted index ranking"
python -m unittest discover -s tests -v
```

The index is stored at `.retrivix/index.json` by default. Supported inputs are `.txt`, `.md`, and `.rst`. Files are read as UTF-8.

## Commands
- `index PATH [--index PATH]`: recursively index supported files.
- `search QUERY [--index PATH] [--limit N]`: rank documents using BM25.
- `stats [--index PATH]`: show document and term counts.

## Design
1. Normalize text to lowercase alphanumeric tokens.
2. Build postings lists from terms to document IDs and term frequencies.
3. Compute BM25 scores with corpus document frequency and average document length.
4. Persist source text and index metadata as JSON so searches can be run offline.

BM25 parameters default to (k_1=1.5), (b=0.75). This is a learning-scale engine, not a replacement for Lucene; it does not yet implement incremental updates, stemming, phrase queries, or distributed indexing.

## Example
```bash
python retrivix.py index examples
python retrivix.py search "database write ahead log"
```

## Project status
Working local MVP. Tests cover tokenization, indexing, persistence, and ranking.