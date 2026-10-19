#!/usr/bin/env python3
"""Retrivix: a dependency-free BM25 full-text search engine."""
from __future__ import annotations
import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9]+")
SUPPORTED = {".txt", ".md", ".rst"}

def tokenize(text: str) -> list[str]:
    """Return lowercase alphanumeric tokens."""
    return TOKEN_RE.findall(text.lower())

class SearchIndex:
    def __init__(self, documents: dict[str, str] | None = None):
        self.documents = documents or {}
        self.lengths: dict[str, int] = {}
        self.postings: dict[str, dict[str, int]] = {}
        self._build()

    def _build(self) -> None:
        postings: dict[str, dict[str, int]] = defaultdict(dict)
        self.lengths = {}
        for doc_id, text in self.documents.items():
            tokens = tokenize(text)
            self.lengths[doc_id] = len(tokens)
            for term, freq in Counter(tokens).items():
                postings[term][doc_id] = freq
        self.postings = dict(postings)

    @property
    def average_length(self) -> float:
        return sum(self.lengths.values()) / len(self.lengths) if self.lengths else 0.0

    def search(self, query: str, limit: int = 10, k1: float = 1.5, b: float = 0.75) -> list[dict]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        terms = tokenize(query)
        if not terms or not self.documents:
            return []
        scores: dict[str, float] = defaultdict(float)
        n_docs = len(self.documents)
        avg_len = self.average_length or 1.0
        for term in terms:
            posting = self.postings.get(term)
            if not posting:
                continue
            df = len(posting)
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            for doc_id, tf in posting.items():
                doc_len = self.lengths[doc_id]
                denominator = tf + k1 * (1 - b + b * doc_len / avg_len)
                scores[doc_id] += idf * (tf * (k1 + 1)) / denominator
        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:limit]
        return [{"id": doc_id, "score": round(score, 6), "text": self.documents[doc_id]} for doc_id, score in ranked]

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"version": 1, "documents": self.documents}, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "SearchIndex":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("version") != 1 or not isinstance(data.get("documents"), dict):
            raise ValueError("Unsupported or invalid Retrivix index file")
        return cls({str(k): str(v) for k, v in data["documents"].items()})

def collect_documents(root: str | Path) -> dict[str, str]:
    path = Path(root)
    if not path.exists():
        raise FileNotFoundError(path)
    files: Iterable[Path] = [path] if path.is_file() else path.rglob("*")
    result = {}
    for file in files:
        if file.is_file() and file.suffix.lower() in SUPPORTED:
            result[str(file.resolve())] = file.read_text(encoding="utf-8", errors="replace")
    return result

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Retrivix local BM25 search")
    sub = parser.add_subparsers(dest="command", required=True)
    p_index = sub.add_parser("index", help="index a directory or file")
    p_index.add_argument("path")
    p_index.add_argument("--index", default=".retrivix/index.json")
    p_search = sub.add_parser("search", help="search the saved index")
    p_search.add_argument("query")
    p_search.add_argument("--index", default=".retrivix/index.json")
    p_search.add_argument("--limit", type=int, default=10)
    p_stats = sub.add_parser("stats", help="show index statistics")
    p_stats.add_argument("--index", default=".retrivix/index.json")
    args = parser.parse_args(argv)
    if args.command == "index":
        docs = collect_documents(args.path)
        SearchIndex(docs).save(args.index)
        print(f"Indexed {len(docs)} documents into {args.index}")
    elif args.command == "search":
        index = SearchIndex.load(args.index)
        results = index.search(args.query, args.limit)
        if not results:
            print("No matching documents.")
        for rank, item in enumerate(results, 1):
            print(f"{rank}. [{item['score']:.4f}] {item['id']}")
            print("   " + " ".join(item["text"].split())[:240])
    else:
        index = SearchIndex.load(args.index)
        print(f"documents={len(index.documents)} terms={len(index.postings)} avg_length={index.average_length:.2f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
