from tools import search_listings

results = search_listings(
    "vintage graphic tee",
    size=None,
    max_price=30
)

print(f"Found {len(results)} results")


print(results)
if results:
    print(results[0]["title"])
    print(results[0]["price"])