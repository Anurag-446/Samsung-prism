"""Unit tests for catalog loader and fingerprinting."""

from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.data.fingerprints import compute_sha256_string


def test_deeplink_catalog_fallback():
    catalog = load_deeplink_catalog(None)
    assert len(catalog) >= 5
    assert catalog.fingerprint != ""

    # Test exact URI resolution
    uri = catalog.resolve_exact_uri("dl_battery_01")
    assert uri == "bixby://com.samsung.android.settings.battery/BatteryProtectionActivity"


def test_catalog_searchable_text_excludes_uri():
    catalog = load_deeplink_catalog(None)
    record = catalog.get_by_id("dl_location_01")
    assert record is not None
    search_text = record.get_searchable_text()

    # Search text MUST NOT contain the bixby:// URI string (P0-08 requirement)
    assert "bixby://" not in search_text
    assert "com.samsung.android.settings.location" not in search_text
    assert "Location permissions" in search_text
