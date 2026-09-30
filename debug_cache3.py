import json
from fixgraph.service.troubleshoot import TroubleshootService
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.query.fast_features import extract_fast_features
from fixgraph.contracts.internal import CaseSignature
from fixgraph.config import settings

catalog = load_deeplink_catalog(settings.get_resolved_path(settings.deeplinks_path))
service = TroubleshootService(catalog=catalog, cache_db_path="data/cache.db")

misses = [
    "My tablet screen stays completely blank when I try to use Data Transfer to scan the QR code for transferring data from my Nexa X1 phone, so the transfer can't proceed."
]

for q in misses:
    req = TroubleshootRequest(query=q, siis_response=None)
    # Re-run normalizer to get hash
    norm_query = service.normalizer.normalize(q)
    
    fast_features = extract_fast_features(norm_query)
    temp_atom = fast_features.to_symptom_atom()
    signature = service.sig_generator.generate_signature(temp_atom)
    runtime_fp = service._generate_runtime_fingerprint()
    
    current_dim = len(service.cache_matcher.embedder.encode_single(q))
    
    all_entries = service.cache_store.get_all_entries()
    print(f"Total entries: {len(all_entries)}")
    for entry in all_entries:
        pipeline_compat = service.cache_matcher.compatibility_validator.validate_pipeline(entry, runtime_fp)
        if not pipeline_compat.compatible:
            print(f"Pipeline incompat: {pipeline_compat.hard_failures}")
            continue

        if entry.embedding_dimension != current_dim or len(entry.query_embedding) != current_dim:
            print("Dim mismatch")
            continue

        try:
            cached_signature_dict = json.loads(entry.canonical_signature_json)
            cached_signature = CaseSignature.model_validate(cached_signature_dict)
        except Exception:
            print("Corrupt entry")
            continue

        semantic_compat = service.cache_matcher.compatibility_validator.validate_semantics(cached_signature, signature)
        if not semantic_compat.compatible:
            print(f"Semantic incompat: {semantic_compat.hard_failures}")
            continue

        print(f"CANDIDATE FOUND: {entry.cache_id}")
