# WikiSearch

WikiSearch is a scalable search engine built over the English Wikipedia dump, implementing a full information retrieval pipeline using disk-based indexing and BM25 ranking. The system is designed to handle datasets that exceed memory limits by leveraging external-memory algorithms.

---

## Overview

This project demonstrates the design and implementation of a large-scale search system capable of indexing and querying millions of documents efficiently. It emphasizes scalability, efficient disk I/O, and practical information retrieval techniques used in real-world search engines.

---

## System Architecture

The pipeline consists of the following stages:

1. **Parsing**
   - Streams and processes compressed Wikipedia dumps
   - Extracts article titles and content
   - Filters redirects and non-content pages

2. **Cleaning and Chunking**
   - Removes markup (templates, HTML, references)
   - Splits documents into overlapping chunks for better retrieval

3. **Indexing (SPIMI)**
   - Builds partial inverted indices in memory
   - Writes sorted blocks to disk

4. **Merging**
   - Performs k-way merge of block files
   - Produces a final inverted index
   - Stores term offsets for fast lookup

5. **Querying**
   - Tokenizes and normalizes user queries
   - Retrieves postings via offset-based access
   - Applies BM25 scoring
   - Aggregates chunk-level scores to document level

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Yash-Bharuntia/WikiSearch.git
cd WikiSearch
```


Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Parse Wikipedia Dump

```bash
python bz2_jsonl.py
```

### 2. Build Index (SPIMI)

```bash
python spimi.py
```

### 3. Merge Blocks

```bash
python merge_blocks.py
```

### 4. Run Search Interface

```bash
python main.py
```

---

## Requirements

* Python 3.10+
* lxml
* zstandard

---

## Key Concepts

* Inverted Index
* BM25 Ranking Function
* External Merge Sort
* SPIMI (Single-Pass In-Memory Indexing)
* Disk-based Retrieval Systems

---

## Technical Highlights

- Designed for datasets larger than available RAM using external-memory algorithms
- Achieves efficient retrieval via offset-based disk access
- Implements BM25 ranking, a standard in modern search engines
- Modular pipeline separating parsing, indexing, and querying

---

## Limitations

* Uses JSON format for index storage, which is not space-optimal
* No index compression (e.g., gap encoding, variable-byte encoding)
* No skip pointers for faster postings traversal
* No semantic or embedding-based retrieval

---

## Future Improvements

* Web Application Extension
* Compressed inverted index (binary format)
* Skip lists for faster query evaluation
* Phrase and proximity search
* Query caching and optimization
* Semantic search using vector embeddings

---

## License
This project is for educational and research purposes.
