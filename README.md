# COMP3011 Search Engine & Polite Web Crawler

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)

A production-grade, in-memory search engine and polite web crawler built from scratch in Python. This project demonstrates highly optimized data structures, advanced Information Retrieval (IR) algorithms, and robust fault-tolerance.

## Key Features (Advanced Implementation)

### 1. Algorithmic Search & Ranking
* **TF-IDF Scoring:** Calculates Term Frequency-Inverse Document Frequency mathematically to rank highly relevant pages over generic matches.
* **Phrase Proximity Bonuses:** Analyzes positional data arrays in $O(1)$ lookup time to award $+10.0$ score bonuses when queried words appear adjacently in the source text.
* **Exact Match Bonuses:** Awards $+5.0$ bonuses to pages containing the exact literal string to prioritize them over stemmed variants.

### 2. Natural Language Processing (NLP)
* **Dynamic Levenshtein Spell-Checking:** Implements Dynamic Programming (DP) to calculate minimum edit distances. If a user typos a query (e.g., `qoote`), the engine mathematically calculates the closest index key and offers a "Did you mean?" suggestion.
* **Custom English Stemmer:** Reduces vocabulary mismatch by safely stripping common suffixes (`-ing`, `-ed`, `-s`) while implementing double-consonant grammar guards and semantic exception lists (e.g., protecting `ring` and `feed`).
* **Optimized Stop-Word Removal:** Filters useless mathematical noise using a class-level, memory-optimized $O(1)$ Hash Set.

### 3. Bulletproof Architecture
* **Idempotent Data Entry:** The inverted index utilizes `Set` lookups to strictly prevent data duplication or skewed TF-IDF math if the crawler loops.
* **Spider-Trap Prevention:** The crawler maintains a `visited` set to automatically break infinite redirect loops.
* **Malformed Data Guards:** Gracefully handles dead pagination links, dropped network packets, and missing HTML tags without crashing.

## Performance Benchmarking

Complexity analysis proves the engine maintains near constant-time retrieval speeds even under massive scale. Testing 50,000 documents results in sub-30ms response times. 

*Build Time complexity is strictly $O(N)$. Levenshtein suggestion complexity is strictly $O(V)$ where V is total unique vocabulary.*

| Docs Indexed | Peak RAM (MB) | Build Time | Query Type | Avg Search (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **1,000** | 11.01 | 0.26s | Single Word | 2.79 ms |
| | | | Multi-Word (AND) | 8.16 ms |
| | | | Typo (Levenshtein)| 2.79 ms |
| **10,000** | 100.97 | 2.97s | Single Word | 4.20 ms |
| | | | Multi-Word (AND) | 8.66 ms |
| | | | Typo (Levenshtein)| 3.95 ms |
| **50,000** | 513.00 | 15.06s| Single Word | 12.13 ms |
| | | | Multi-Word (AND) | 24.74 ms |
| | | | Typo (Levenshtein)| 2.60 ms |

## Installation & Usage

1. Clone the repository and install requirements:
```bash
git clone https://github.com/AliKhairy/COMP3011_Coursework2
pip install -r requirements.txt
```

2. Launch the interactive search shell:
```bash
python -m src.main
```

3. Available Commands:
* `build`: Crawls the target website and constructs the inverted index.
* `load`: Loads a previously saved index from the hard drive (`data/index.json`).
* `find <query>`: Executes a TF-IDF ranked search with stem expansion.
* `print <word>`: Prints raw index statistics and positional data for a specific word.
* `quit`: Exits the application.

## Testing Coverage

This project maintains an **88% test coverage** suite via `pytest`, enforcing strict CI/CD pipeline integrity. 
The test suite utilizes advanced `unittest.mock` patching, `capsys` terminal interception, and `tmp_path` isolated file system fixtures to verify:
* Spider-trap infinite loop breakage.
* Stemmer destruction prevention (e.g., ensuring "feed" does not become "fe").
* Zero-score TF-IDF mathematical proofs.
* Idempotency state validation.

Run the test suite locally:
```bash
python -m pytest tests/ --cov=src/ --cov-report=term-missing
```
