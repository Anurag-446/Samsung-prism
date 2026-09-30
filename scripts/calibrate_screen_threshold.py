"""Script to calibrate the screen resolver threshold."""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fixgraph.bootstrap import build_catalog, build_challenge_assets
from fixgraph.config import settings
from fixgraph.navigation.resolver import NavigationAwareScreenResolver

def main():
    assets = build_challenge_assets(settings, "development")
    catalog = build_catalog(settings, assets, "development")
    
    resolver = NavigationAwareScreenResolver(catalog)
    
    test_queries = [
        ("Wi-Fi network drops", "dl_wifi_01", True),
        ("Turn on bluetooth", "dl_bluetooth_01", True),
        ("Battery is dying fast", "dl_battery_01", True),
        ("Screen is too bright", "dl_display_01", True),
        ("How do I clean my phone?", None, False),
        ("My camera is broken", None, False)
    ]
    
    print("Testing fusion thresholds:")
    for query, expected_id, should_match in test_queries:
        top = resolver.resolve_action_intent(query)
        if not top:
            print(f"'{query}': No match (Expected: {expected_id})")
        else:
            match_status = "CORRECT" if top.catalog_record_id == expected_id else "INCORRECT"
            print(f"'{query}': Matched {top.catalog_record_id} with conf {top.confidence:.3f} | Dense: {top.dense_score:.3f} | BM25: {top.bm25_score:.3f} ({match_status})")

if __name__ == "__main__":
    main()
