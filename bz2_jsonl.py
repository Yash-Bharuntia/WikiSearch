import bz2
import json
import zstandard as zstd
from lxml import etree
from regex_pat import clean_text

INPUT_FILE = "WikiDumps//Input//enwiki-2026-04-01-p10p1141529.xml.bz2"
OUTPUT_FILE = "WikiDumps//Output//output_new.jsonl.zst"
DOC_STORE_FILE = "doc_store.jsonl"

LIMIT = None   

def is_redirect(text):
    if not text:
        return False
    t = text.strip().lower()
    return t.startswith("#redirect") or t.startswith("redirect")


def chunk_text(words, chunk_size=300, overlap=50):
    chunks = []
    step = chunk_size - overlap

    for i in range(0, len(words), step):
        chunk = words[i:i + chunk_size]
        if len(chunk) < 50:
            continue
        chunks.append(" ".join(chunk))

    return chunks


# XML streaming
context = etree.iterparse(
    bz2.open(INPUT_FILE, "rb"),
    events=("end",),
    tag="{*}page"
)

cctx = zstd.ZstdCompressor()

doc_offsets = {}
count = 0

with open(OUTPUT_FILE, "wb") as compressed_out, \
     open(DOC_STORE_FILE, "w", encoding="utf-8") as doc_out:

    with cctx.stream_writer(compressed_out) as writer:

        for _, elem in context:

            title = elem.findtext("{*}title")
            if not title or ":" in title:
                elem.clear()
                continue

            page_id = elem.findtext("./{*}id") or ""

            text_elem = elem.find("{*}revision/{*}text")
            text = text_elem.text if text_elem is not None and text_elem.text else ""

            if is_redirect(text):
                elem.clear()
                continue

            text = clean_text(text)
            words = text.split()

            if len(words) < 100:
                elem.clear()
                continue

            chunks = chunk_text(words)

            for idx, chunk in enumerate(chunks):
                doc_id = f"{page_id}_{idx}"

                record = json.dumps({
                    "id": doc_id,
                    "title": title,
                    "text": chunk[:500]
                }, ensure_ascii=False) + "\n"

                encoded = record.encode("utf-8")

                # Write compressed
                writer.write(encoded)

                # Write uncompressed doc store with offsets
                offset = doc_out.tell()
                doc_offsets[doc_id] = offset
                doc_out.write(record)

            count += 1
            if LIMIT is not None and count >= LIMIT:
                break

            # memory cleanup
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]


# Save doc offsets
with open("doc_offsets.json", "w", encoding="utf-8") as f:
    json.dump(doc_offsets, f)

print("Parsing complete.")