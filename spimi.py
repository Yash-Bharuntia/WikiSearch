import zstandard as zstd
import json
import io
from collections import defaultdict, Counter
from tokenizer import tokenize
from write_blocks_disk import write_block, BLOCK_SIZE


# CONFIG
INPUT_FILE = "WikiDumps//Output//output_new.jsonl.zst"

# SPIMI BLOCK BUILDING
dctx = zstd.ZstdDecompressor()

index = defaultdict(list)
doc_length = {}

block_id = 0
doc_counter = 0

with open(INPUT_FILE, "rb") as f:
    with dctx.stream_reader(f) as reader:
        text_stream = io.TextIOWrapper(reader, encoding="utf-8")

        for line in text_stream:
            data = json.loads(line)

            doc_id = data['id']
            text = data['text']

            #Tokenize
            tokens = tokenize(text)

            #Store doc length
            doc_length[doc_id] = len(tokens)

            #Term frequency
            tf = Counter(tokens)

            #Build index
            for term, freq in tf.items():
                index[term].append((doc_id, freq))

            doc_counter += 1

            #BLOCK FLUSH CONDITION
            if doc_counter >= BLOCK_SIZE:
                write_block(index, block_id)

                # Reset for next block
                index = defaultdict(list)
                doc_counter = 0
                block_id += 1

        # BLOCK FLUSH 
        if index:
            write_block(index, block_id)

print(f"Total blocks created: {block_id + 1}")