import json
from fixgraph.service.troubleshoot import TroubleshootService
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.data.deeplink_catalog import DeeplinkCatalog
from fixgraph.query.fast_features import extract_fast_features

catalog = DeeplinkCatalog(records=[])
service = TroubleshootService(catalog=catalog, cache_db_path="data/cache.db")

misses = [
    "My tablet screen stays completely blank when I try to use Data Transfer to scan the QR code for transferring data from my Nexa X1 phone, so the transfer can't proceed.",
    "My Nexa Fold X1 inner screen stopped working by itself; it shows no image and doesn't respond to touch, while the outer cover screen still works.",
    "My TechCorp Nexa Fold X1 screen flickers and goes blank whenever I open it, so I can't see anything or access the settings, which stops me from using the phone.",
    "My Nexa Fold X1 screen is half blackone side of the display is completely dark while the other side works fine, so I can't access the device normally.",
    "My Nexa X1 Ultra screen is completely black and won't turn on, even though the phone powers on, rings, and otherwise works; there is no physical damage."
]

for q in misses:
    req = TroubleshootRequest(query=q, siis_response=None)
    # Re-run normalizer to get hash
    norm_query = service.normalizer.normalize(q)
    
    fast_features = extract_fast_features(norm_query)
    temp_atom = fast_features.to_symptom_atom()
    signature = service.sig_generator.generate_signature(temp_atom)
    runtime_fp = service._generate_runtime_fingerprint()
    
    entry, sim, reason = service.cache_matcher.lookup(signature, q, runtime_fp)
    print(f"Query: {q[:30]}... | Sim: {sim:.4f} | Reason: {reason}")
