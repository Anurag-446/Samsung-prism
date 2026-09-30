"""Unit tests for catalog loader and fingerprinting."""

import pytest

from fixgraph.data.loaders import CatalogValidationError, load_deeplink_catalog


def test_deeplink_catalog_loads_fixture():
    catalog = load_deeplink_catalog("tests/fixtures/challenge_assets/deeplinks.json")
    assert len(catalog) >= 5
    assert catalog.fingerprint != ""

    # Test exact URI resolution
    uri = catalog.resolve_exact_uri("dl_battery_01")
    assert uri == "bixby://com.samsung.android.settings.battery/BatteryProtectionActivity"


def test_catalog_searchable_text_excludes_uri():
    catalog = load_deeplink_catalog("tests/fixtures/challenge_assets/deeplinks.json")
    record = catalog.get_by_id("dl_location_01")
    assert record is not None
    search_text = record.get_searchable_text()

    # Search text MUST NOT contain the bixby:// URI string (P0-08 requirement)
    assert "bixby://" not in search_text
    assert "com.samsung.android.settings.location" not in search_text
    assert "Location permissions" in search_text


def test_missing_file_fails():
    with pytest.raises(CatalogValidationError, match="not found"):
        load_deeplink_catalog("tests/fixtures/does_not_exist.json")


def test_malformed_json_fails(tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{malformed: true")
    with pytest.raises(CatalogValidationError, match="Invalid JSON"):
        load_deeplink_catalog(bad_json)


def test_empty_catalog_fails(tmp_path):
    empty_json = tmp_path / "empty.json"
    empty_json.write_text("[]")
    with pytest.raises(CatalogValidationError, match="is empty"):
        load_deeplink_catalog(empty_json)


def test_missing_uri_fails(tmp_path):
    bad_data = tmp_path / "missing_uri.json"
    bad_data.write_text('[{"id": "test1"}]')
    with pytest.raises(CatalogValidationError, match="missing a deeplink URI"):
        load_deeplink_catalog(bad_data)


def test_duplicate_id_fails(tmp_path):
    dup_data = tmp_path / "dup.json"
    dup_data.write_text('[{"id": "test1", "uri": "a"}, {"id": "test1", "uri": "b"}]')
    with pytest.raises(CatalogValidationError, match="Duplicate record ID"):
        load_deeplink_catalog(dup_data)
