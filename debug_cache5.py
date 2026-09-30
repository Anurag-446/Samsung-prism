import json
from fixgraph.service.troubleshoot import TroubleshootService
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.config import settings
from fixgraph.contracts.internal import ValidationContext

catalog = load_deeplink_catalog(settings.get_resolved_path(settings.deeplinks_path))
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
    norm_query = service.normalizer.normalize(q)
    
    fast_features = service.symptom_parser.parse_fast(norm_query)
    temp_atom = fast_features.to_symptom_atom()
    signature = service.sig_generator.generate_signature(temp_atom)
    runtime_fp = service._generate_runtime_fingerprint()
    
    entry, sim, reason = service.cache_matcher.lookup(signature, norm_query.clean_query, runtime_fp)
    
    if entry:
        val_ctx = ValidationContext(
            request_id="test",
            original_query_hash="test",
            case_signature=signature,
            catalog_fingerprint=runtime_fp.catalog_sha256,
            pipeline_fingerprint=runtime_fp.composite_sha256,
            prohibited_actions=temp_atom.constraints.prohibited_actions,
            completed_actions=temp_atom.constraints.completed_actions
        )
        cached_goal_dict = json.loads(entry.validated_plan_json)
        from fixgraph.contracts.internal import Goal
        cached_goal = Goal.model_validate(cached_goal_dict)
        val_report = service.final_gate.validate(cached_goal, val_ctx)
        print(f"Query: {q[:30]} | Valid: {val_report.valid} | Errors: {[e.message for e in val_report.errors]}")
    else:
        print(f"Query: {q[:30]} | No entry | Reason: {reason}")
