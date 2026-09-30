"""Unit tests for retrieval index, hybrid fusion, and screen resolver."""

from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.retrieval.bm25_index import BM25Index
from fixgraph.retrieval.dense_index import DenseIndex
from fixgraph.retrieval.screen_resolver import ScreenResolver


def test_bm25_retrieval():
    catalog = load_deeplink_catalog("tests/fixtures/challenge_assets/deeplinks.json")
    bm25 = BM25Index(catalog)
    results = bm25.search("battery protection fast drain power save", top_k=3)
    assert len(results) > 0
    top_rec = results[0][0]
    assert "battery" in top_rec.name.lower() or "battery" in top_rec.description.lower()


def test_dense_retrieval():
    catalog = load_deeplink_catalog("tests/fixtures/challenge_assets/deeplinks.json")
    dense = DenseIndex(catalog)
    results = dense.search("turn on location services permissions", top_k=3)
    assert len(results) > 0
    top_rec = results[0][0]
    assert "location" in top_rec.name.lower() or "location" in top_rec.description.lower()


def test_hybrid_screen_resolver():
    catalog = load_deeplink_catalog("tests/fixtures/challenge_assets/deeplinks.json")
    resolver = ScreenResolver(catalog)

    # Test battery screen resolution
    candidate = resolver.resolve_action_intent(
        "Configure battery saver mode and protect battery health"
    )
    assert candidate is not None
    assert candidate.catalog_record_id == "dl_battery_01"
    assert (
        candidate.exact_uri
        == "bixby://com.samsung.android.settings.battery/BatteryProtectionActivity"
    )

    # Test location screen resolution
    candidate = resolver.resolve_action_intent("Location permissions and GPS accuracy")
    assert candidate is not None
    assert candidate.catalog_record_id == "dl_location_01"
    assert (
        candidate.exact_uri
        == "bixby://com.samsung.android.settings.location/LocationSettingsActivity"
    )
