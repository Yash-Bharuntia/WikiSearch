import json
import os
import zstandard as zstd

BLOCK_SIZE = 50000


def write_block(index, block_id, output_dir="Blocks"):
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"block_{block_id}.jsonl.zst")

    print(f"Writing block {block_id} with {len(index)} terms...")

    cctx = zstd.ZstdCompressor()

    with open(file_path, "wb") as f:
        with cctx.stream_writer(f) as writer:

            for term in sorted(index.keys()):
                postings = index[term]

                merged = {}
                for doc_id, tf in postings:
                    merged[doc_id] = merged.get(doc_id, 0) + tf

                sorted_postings = sorted(merged.items())

                entry = {
                    "term": term,
                    "postings": sorted_postings
                }

                writer.write((json.dumps(entry) + "\n").encode("utf-8"))