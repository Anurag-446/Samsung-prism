from fixgraph.cache.store import CaseCacheStore
from fixgraph.query.normalizer import QueryNormalizer
import json

cases = json.load(open('eval/retrieval/manager_screen_cases.json'))
store = CaseCacheStore('data/cache.db')
normalizer = QueryNormalizer()

entries = store.get_all_entries()

for case in cases[:50]:
    query = case['query']
    norm = normalizer.normalize(query).clean_query
    found = False
    for e in entries:
        if e.canonical_query == norm:
            found = True
            break
    if not found:
        print(f"Query missing entirely from cache: {query}")
