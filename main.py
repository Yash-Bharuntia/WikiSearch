import json
from querying import search

with open("doc_length.json", "r") as f:
    doc_length = json.load(f)

with open("meta.json", "r") as f:
    meta = json.load(f)

N = meta["N"]
avg_dl = meta["avg_dl"]

print("=== WikiSearch CLI ===")
print("Type 'exit' to quit\n")

while True:
    query = input("Search> ").strip()

    if query.lower() in ["exit", "quit"]:
        break

    results = search(query, doc_length, avg_dl, N)

    if not results:
        print("No results found.\n")
        continue

    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r['title']}")
        print(f"Score: {r['score']:.4f}")
        print(f"{r['snippet']}")

    print("\n" + "-" * 60)