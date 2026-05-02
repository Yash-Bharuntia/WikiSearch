import json
import math
import heapq
from tokenizer import tokenize

INDEX_FILE = "final_index.jsonl"
DOC_STORE_FILE = "doc_store.jsonl"

# LOAD OFFSETS
with open("term_offsets.json", "r") as f:
    term_offsets = json.load(f)

with open("doc_offsets.json", "r") as f:
    doc_offsets = json.load(f)

# FILE HANDLES (avoid reopening)
index_file = open(INDEX_FILE, "r", encoding="utf-8")
doc_file = open(DOC_STORE_FILE, "r", encoding="utf-8")

# GET POSTINGS (O(1))
def get_postings(term):
    if term not in term_offsets:
        return None

    offset = term_offsets[term]
    index_file.seek(offset)
    return json.loads(index_file.readline())

# GET DOCUMENT (O(1))
def get_document(doc_id):
    if doc_id not in doc_offsets:
        return None

    offset = doc_offsets[doc_id]
    doc_file.seek(offset)
    return json.loads(doc_file.readline())

# QUERY NORMALIZATION
def normalize_query(query):
    query = query.lower()

    remove_words = {
        "what", "is", "the", "who", "define",
        "a", "an", "of", "in"
    }

    tokens = query.split()
    tokens = [t for t in tokens if t not in remove_words]

    return " ".join(tokens)

# BM25 PARAMETERS
k1 = 1.5
b = 0.75

TITLE_BOOST = 2.5
EXACT_MATCH_BOOST = 5.0
MULTI_TERM_BOOST = 1.2

# BM25 SCORING + BOOSTS
def bm25_score(query_tokens, doc_length, avg_dl, N):
    scores = {}

    for term in query_tokens:
        entry = get_postings(term)
        if not entry:
            continue

        df = entry["df"]
        postings = entry["postings"]

        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)

        for doc_id, tf in postings:
            dl = doc_length.get(doc_id, 1)

            denom = tf + k1 * (1 - b + b * dl / avg_dl)
            score = idf * (tf * (k1 + 1)) / denom

            scores[doc_id] = scores.get(doc_id, 0) + score

    return scores

# AGGREGATE CHUNKS → DOC
def get_base_doc_id(chunk_id):
    return chunk_id.split("_")[0]

def aggregate_scores(scores):
    doc_scores = {}
    best_chunk = {}

    for chunk_id, score in scores.items():
        base_id = get_base_doc_id(chunk_id)

        if base_id not in doc_scores or score > doc_scores[base_id]:
            doc_scores[base_id] = score
            best_chunk[base_id] = chunk_id

    return doc_scores, best_chunk

# APPLY BOOSTS (CRITICAL)
def apply_boosts(doc_scores, best_chunk, query_tokens, raw_query):
    boosted_scores = {}

    for doc_id, score in doc_scores.items():
        chunk_id = best_chunk[doc_id]
        doc = get_document(chunk_id)

        if not doc:
            continue

        title = doc["title"].lower()
        text = doc["text"].lower()

        #TITLE BOOST
        for term in query_tokens:
            if term in title:
                score *= TITLE_BOOST

        #EXACT TITLE MATCH
        if raw_query == title:
            score += EXACT_MATCH_BOOST

        #MULTI-TERM BONUS
        if all(term in text for term in query_tokens):
            score *= MULTI_TERM_BOOST

        boosted_scores[doc_id] = score

    return boosted_scores

# TOP-K
def top_k(doc_scores, k=5):
    return heapq.nlargest(k, doc_scores.items(), key=lambda x: x[1])

# SEARCH
def search(query, doc_length, avg_dl, N, k=5):
    raw_query = query.lower()

    #normalize query
    query = normalize_query(query)
    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    #BM25
    scores = bm25_score(query_tokens, doc_length, avg_dl, N)

    #chunk → doc
    doc_scores, best_chunk = aggregate_scores(scores)

    #apply boosts
    doc_scores = apply_boosts(doc_scores, best_chunk, query_tokens, raw_query)

    #rank
    top_docs = top_k(doc_scores, k)

    results = []

    for doc_id, score in top_docs:
        chunk_id = best_chunk[doc_id]
        doc = get_document(chunk_id)

        if not doc:
            continue

        results.append({
            "title": doc["title"],
            "score": score,
            "snippet": doc["text"][:200]
        })

    return results