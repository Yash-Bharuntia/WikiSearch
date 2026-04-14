import bz2
import re
import json
import zstandard as zstd
from lxml import etree
from regex_pat import (
    COMMENT_RE, REF_RE, REF_SELF_RE, TEMPLATE_RE, TABLE_RE, FILE_RE, LINK_TEXT_RE, LINK_RE, FORMAT_RE, HEADER_RE, HTML_RE,
    BULLET_RE, URL_RE, TEMPLATE_LEFTOVER_RE, INFOBOX_RE, TABLE_ROW_RE, MATH_RE, WHITESPACE_RE, clean_text
)

INPUT_FILE = "WikiDumps//Input//enwiki-2026-04-01-p10p1141529.xml.bz2"
OUTPUT_FILE = "WikiDumps//Output//output_new.jsonl.zst"

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

context = etree.iterparse(
    bz2.open(INPUT_FILE, "rb"),
    events=("end",),
    tag="{*}page"
)

LIMIT = 100000
count = 0

cctx = zstd.ZstdCompressor()

with open(OUTPUT_FILE, "wb") as out:
    with cctx.stream_writer(out) as writer:
        for _, elem in context:
            
            # Extract title 
            title = elem.findtext("{*}title")
            if not title or ":" in title:
                elem.clear()
                continue

            # Extract page ID
            page_id = elem.findtext("./{*}id") or ""

            # Extract text 
            text_elem = elem.find("{*}revision/{*}text")
            text = text_elem.text if text_elem is not None and text_elem.text else ""

            # Skip redirects early
            if is_redirect(text):
                elem.clear()
                continue

            # Clean text
            text = clean_text(text)

            words = text.split()

            # Skip  small documents
            if len(words) < 100:
                elem.clear()
                continue

            # Chunking
            chunks = chunk_text(words)

            # Write JSONL
            for idx, chunk in enumerate(chunks):
                writer.write((json.dumps({
                    "id": f"{page_id}_{idx}",
                    "title": title,
                    "text": chunk
                }, ensure_ascii=False) + "\n").encode("utf-8"))

            count += 1
            if count >= LIMIT:
                break
            
            # Memory cleanup
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]