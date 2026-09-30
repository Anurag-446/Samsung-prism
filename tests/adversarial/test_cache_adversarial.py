import os

import pytest

from fixgraph.config import settings
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.service.troubleshoot import TroubleshootService

HARD_NEGATIVES = [
    ("battery drains fast", "battery won't charge"),
    ("battery drains fast", "phone overheats"),
    ("screen flickers", "screen timeout too short"),
    ("screen flickers", "brightness too low"),
    ("camera blurry", "camera permission denied"),
    ("wifi disconnects", "mobile data disconnected"),
    ("wifi slow", "wifi not connecting"),
    ("location inaccurate", "location permission denied"),
    ("Bluetooth won't pair", "Bluetooth audio stutters"),
    ("phone slow", "storage nearly full"),
    ("charging slow", "battery drains quickly"),
]

@pytest.fixture(scope="module")
def service():
    db_path = "data/adversarial_cache.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    catalog = load_deeplink_catalog(settings.deeplinks_path)
    svc = TroubleshootService(catalog=catalog, cache_db_path=db_path)

    # Warm cache with canonical positive cases
    for pos, _ in HARD_NEGATIVES:
        req = TroubleshootRequest(query=pos)
        svc.troubleshoot(req)

    yield svc

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except:
            pass

def test_cache_hard_negatives(service):
    false_hits = []

    for _, neg in HARD_NEGATIVES:
        req = TroubleshootRequest(query=neg)
        outcome = service.troubleshoot(req)
        metrics = outcome.metrics

        # A hard negative should NOT result in a cache hit, despite semantic similarity
        if metrics.cache_hit:
            false_hits.append(neg)

    assert len(false_hits) == 0, f"False hits detected for hard negatives: {false_hits}"
