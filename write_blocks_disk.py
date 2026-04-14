import json

BLOCK_SIZE = 5000 


# WRITE BLOCK TO DISK
def write_block(index, block_id):
    print(f"Writing block {block_id} with {len(index)} terms...")
    
    with open(f"Blocks/block_{block_id}.jsonl", "w", encoding="utf-8") as f:
        for term in sorted(index.keys()):
            entry = {
                "term": term,
                "postings": index[term]
            }
            f.write(json.dumps(entry) + "\n")

