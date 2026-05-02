import json
import heapq
import os
import zstandard as zstd
from collections import defaultdict

BLOCK_DIR = "Blocks"
OUTPUT_FILE = "final_index.jsonl"

def open_block(path):
    f = open(path, "rb")
    dctx = zstd.ZstdDecompressor()
    reader = dctx.stream_reader(f)
    return f, reader

block_streams = []

for fname in os.listdir(BLOCK_DIR):
    if fname.endswith(".zst"):
        f, reader = open_block(os.path.join(BLOCK_DIR, fname))
        block_streams.append((f, reader))

def read_line(reader):
    line = b""
    while True:
        c = reader.read(1)
        if not c:
            break
        if c == b"\n":
            break
        line += c
    return line.decode("utf-8") if line else None

heap = []

for i, (f, reader) in enumerate(block_streams):
    line = read_line(reader)
    if line:
        data = json.loads(line)
        heapq.heappush(heap, (data["term"], i, data["postings"]))

def merge_postings(postings):
    merged = defaultdict(int)
    for doc_id, tf in postings:
        merged[doc_id] += tf
    return list(merged.items())

term_offset = {}

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

    current_term = None
    current_postings = []

    while heap:
        term, file_id, postings = heapq.heappop(heap)

        if term != current_term:
            if current_term is not None:
                merged = merge_postings(current_postings)
                merged.sort()

                offset = out.tell()
                term_offset[current_term] = offset

                out.write(json.dumps({
                    "term": current_term,
                    "df": len(merged),
                    "postings": merged
                }) + "\n")

            current_term = term
            current_postings = postings.copy()

        else:
            current_postings.extend(postings)

        f, reader = block_streams[file_id]
        line = read_line(reader)

        if line:
            data = json.loads(line)
            heapq.heappush(heap, (data["term"], file_id, data["postings"]))

    # final flush
    if current_term:
        merged = merge_postings(current_postings)
        merged.sort()

        offset = out.tell()
        term_offset[current_term] = offset

        out.write(json.dumps({
            "term": current_term,
            "df": len(merged),
            "postings": merged
        }) + "\n")

with open("term_offsets.json", "w") as f:
    json.dump(term_offset, f)

print("Merge complete.")