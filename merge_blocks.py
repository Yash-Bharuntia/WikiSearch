import json
import heapq
import os

BLOCK_DIR = "Blocks"
OUTPUT_FILE = "final_index.jsonl"

# OPEN ALL BLOCK FILES
block_files = [
    open(os.path.join(BLOCK_DIR, f), "r", encoding="utf-8")
    for f in os.listdir(BLOCK_DIR)
    if f.startswith("block_")
]


# INITIALIZE HEAP
# heap item = (term, block_id, postings)
heap = []

for i, f in enumerate(block_files):
    line = f.readline()
    if line:
        data = json.loads(line)
        heapq.heappush(heap, (data["term"], i, data["postings"]))


# MERGE PROCESS
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

    current_term = None
    current_postings = []

    while heap:
        term, file_id, postings = heapq.heappop(heap)

        # If new term → flush previous
        if current_term != term:
            if current_term is not None:
                out.write(json.dumps({
                    "term": current_term,
                    "postings": current_postings
                }) + "\n")

            current_term = term
            current_postings = postings.copy()
        else:
            # Merge postings
            current_postings.extend(postings)

        # Read next line from same file
        next_line = block_files[file_id].readline()
        if next_line:
            data = json.loads(next_line)
            heapq.heappush(heap, (data["term"], file_id, data["postings"]))

    # Flush last term
    if current_term is not None:
        out.write(json.dumps({
            "term": current_term,
            "postings": current_postings
        }) + "\n")


# CLOSE FILES
for f in block_files:
    f.close()

print("Merging complete to final_index.jsonl")