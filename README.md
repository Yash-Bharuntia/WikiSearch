---

## Installation

Clone the repository:


git clone https://github.com/Yash-Bharuntia/WikiSearch.git

cd WikiSearch


Install dependencies:


pip install -r requirements.txt


---

## Usage

### 1. Parse Wikipedia Dump


python bz2_jsonl.py


### 2. Build Index (SPIMI)


python spimi.py


### 3. Merge Blocks


python merge_blocks.py


### 4. Run Search Interface


python main.py


---

## Requirements

- Python 3.10+
- lxml
- zstandard

---

## Key Concepts

- Inverted Index
- BM25 Ranking Function
- External Merge Sort
- SPIMI (Single-Pass In-Memory Indexing)
- Disk-based Retrieval Systems

---

## Limitations

- Uses JSON format for index storage, which is not space-optimal
- No index compression (e.g., gap encoding, variable-byte encoding)
- No skip pointers for faster postings traversal
- No semantic or embedding-based retrieval

---

## Future Improvements

- Compressed inverted index (binary format)
- Skip lists for faster query evaluation
- Phrase and proximity search
- Query caching and optimization
- Semantic search using vector embeddings

---

## License

This project is for educational and research purposes.
