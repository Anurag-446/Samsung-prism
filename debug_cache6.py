import json
import time
from fixgraph.service.troubleshoot import TroubleshootService
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.query.fast_features import extract_fast_features
from fixgraph.config import settings

settings.cache_semantic_threshold = 0.95
catalog = load_deeplink_catalog(settings.get_resolved_path(settings.deeplinks_path))
service = TroubleshootService(catalog=catalog, cache_db_path="data/cache.db")

with open("eval/retrieval/manager_screen_cases.json") as f:
    cases = json.load(f)

for item in cases:
    q = item["query"]
    req = TroubleshootRequest(query=q, siis_response=None)
    
    norm_query = service.normalizer.normalize(q)
    fast_features = extract_fast_features(norm_query)
    temp_atom = fast_features.to_symptom_atom()
    signature = service.sig_generator.generate_signature(temp_atom)
    runtime_fp = service._generate_runtime_fingerprint()
    
    entry, sim, reason = service.cache_matcher.lookup(signature, norm_query.clean_query, runtime_fp)
    
    if not entry:
        print(f"MISS! Reason: {reason} | Sim: {sim:.4f} | Query: {q[:50]}")
