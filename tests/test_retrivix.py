import tempfile
import unittest
from pathlib import Path
from retrivix import SearchIndex, tokenize, collect_documents

class RetrivixTests(unittest.TestCase):
    def test_tokenize_normalizes(self):
        self.assertEqual(tokenize("Hello, WORLD! v2"), ["hello", "world", "v2"])

    def test_bm25_prefers_relevant_document(self):
        idx = SearchIndex({
            "database.txt": "database storage engine write ahead log",
            "garden.txt": "plants soil water sunlight",
            "search.txt": "search engine inverted index retrieval",
        })
        result = idx.search("database storage")
        self.assertEqual(result[0]["id"], "database.txt")

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.json"
            original = SearchIndex({"a.md": "offline search", "b.md": "database engine"})
            original.save(path)
            loaded = SearchIndex.load(path)
            self.assertEqual(loaded.documents, original.documents)
            self.assertEqual(loaded.search("offline")[0]["id"], "a.md")

    def test_collect_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("hello", encoding="utf-8")
            (root / "ignore.py").write_text("not indexed", encoding="utf-8")
            self.assertEqual(len(collect_documents(root)), 1)

    def test_invalid_limit(self):
        with self.assertRaises(ValueError):
            SearchIndex({"a": "hello"}).search("hello", 0)

if __name__ == "__main__":
    unittest.main()
